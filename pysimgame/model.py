"""The model that runs with the game."""
from __future__ import annotations

import logging
import os
import re
import shutil
import threading
from dataclasses import dataclass
from functools import cached_property, singledispatchmethod
from pathlib import Path
from threading import Lock, Thread
from types import NotImplementedType
from typing import TYPE_CHECKING, Callable, Dict, Iterable, List

import pandas as pd
import pygame

import pysimgame
from pysimgame.actions.actions import BaseAction, Budget, Edict, Policy
from pysimgame.regions_display import RegionComponent
from pysimgame.utils import GameComponentManager

from .utils.logging import logger, logger_enter_exit

if TYPE_CHECKING:
    import pysd

    from .game_manager import GameManager
    from .plots import PlotsManager
    from .types import POLICY_DICT


POLICY_PREFIX = "policy_"
# policy convention
# 1. POLICY_PREFIX
# 2. the name of the policy
# 3. the funciton to replace
# example name: policy_policyname_func_to_replace


class ModelManager(GameComponentManager):
    """Model used to manage the pysd model-s in the simulation.

    Works like a dictionary for the different regions, mapping
    region names to :py:module:`pysd` models of each region.
    It also accepts dictionary of policies where policy apply to
    a model.
    """

    GAME_MANAGER: GameManager
    PLOTS_MANAGER: PlotsManager

    _elements_names: List[str] = None  # Used to internally store elements
    capture_elements: List[str]
    models: Dict[str, pysd.statefuls.Model]
    _model: pysd.statefuls.Model
    time_step: float
    clock: pygame.time.Clock
    fps: float
    doc: pd.DataFrame

    # region Properties
    @cached_property
    def doc(self) -> Dict[str, Dict[str, str]]:
        """Return the documentation of each component.

        The return dictonary contains a dict for each component of the models.
        The subdicts have the following keys:
            Real Name
            Py Name
            Eqn
            Unit
            Lims
            Type
            Subs
            Comment

        Code directly copied and modified from pysd.
        """
        collector = {}
        for name, varname in self._model.components._namespace.items():
            # if varname not in self.capture_elements:
            #     # Ignore variable not in capture elements
            #     continue
            try:
                # TODO correct this when Original Eqn is in several lines
                docstring: str
                docstring = getattr(self._model.components, varname).__doc__
                lines = docstring.split("\n")

                for unit_line in range(3, 9):
                    # this loop detects where Units: starts as
                    # sometimes eqn could be split in several lines
                    if re.findall("Units:", lines[unit_line]):
                        break
                if unit_line == 3:
                    eqn = lines[2].replace("Original Eqn:", "").strip()
                else:
                    eqn = "; ".join(
                        [line.strip() for line in lines[3:unit_line]]
                    )

                collector[varname] = {
                    "Real Name": name,
                    "Py Name": varname,
                    "Eqn": eqn,
                    "Unit": lines[unit_line].replace("Units:", "").strip(),
                    "Lims": lines[unit_line + 1]
                    .replace("Limits:", "")
                    .strip(),
                    "Type": lines[unit_line + 2].replace("Type:", "").strip(),
                    "Subs": lines[unit_line + 3].replace("Subs:", "").strip(),
                    "Comment": "\n".join(lines[(unit_line + 4) :]).strip(),
                }

            except Exception as exp:
                logger.warning(
                    f"Could not parse docstring of '{varname}' due to '{exp}'"
                )
                collector[varname] = {
                    "Real Name": varname,
                    "Py Name": varname,
                    "Eqn": "???",
                    "Unit": "???",
                    "Lims": "???",
                    "Type": "???",
                    "Subs": "???",
                    "Comment": "???",
                }
        logger.debug(f"Doc: {collector}")
        return collector

    @property
    def fps(self):
        """Get the frames per second of the model."""
        return self._fps

    @fps.setter
    def fps(self, new_fps: float):
        if new_fps < 0:
            logger.error(f"FPS must be positive not {new_fps}.")
        else:
            self._fps = new_fps

    @cached_property
    def elements_names(self) -> List[str]:
        """Return the names of the elements simulated in the model.

        Removes some elements that are not interesting for the model
        (time step, start, finish)
        """
        if self._elements_names is None:
            # Reads the first models components
            self._elements_names = list(
                list(self.models.values())[0].components._namespace.values()
            )
            logger.debug(
                f"All the model.components elements: {self._elements_names}"
            )
        elements_names = self._elements_names.copy()
        for val in [
            "time",
            "final_time",
            "saveper",
            "initial_time",
            "time_step",
        ]:
            elements_names.remove(val)
        return elements_names

    @singledispatchmethod
    def __getitem__(self, key):
        raise TypeError(f"Invalid key for type {type(key)}.")

    @__getitem__.register
    def _(self, region: str):
        try:
            return self.models[region]
        except KeyError as keyerr:
            print(self.GAME.REGIONS_DICT)
            raise KeyError(f"{region} not in {self.models.keys()}")

    @__getitem__.register
    def _(self, region: RegionComponent):
        return self[region.name]

    # endregion Properties
    # region Prepare
    def prepare(self):

        self._load_models()
        # Set the captured_elements
        self.capture_elements = None

        # Create the time managers
        self.clock = pygame.time.Clock()

        logger.debug(f"initial_time {self._model.components.initial_time()}.")
        logger.debug(f"time_step {self._model.components.time_step()}.")
        logger.debug(f"final_time {self._model.components.final_time()}.")

        self.time_axis = []
        self.current_time = self._model.time()
        self.current_step = int(0)
        self.time_step = self._model.components.time_step()

        self.fps = self.GAME.SETTINGS.get("FPS", 1)

        regions = self.GAME_MANAGER.game.REGIONS_DICT.keys()
        # Create a df to store the output
        index = pd.MultiIndex.from_product(
            [regions, self.capture_elements],
            names=["regions", "elements"],
        )
        logger.debug(f"Created Index {index}")
        self.outputs = pd.DataFrame(columns=index)
        # Sort the indexes for performance
        self.outputs.sort_index()

        # Finds out all the policies available
        # All possible unique policies
        # self.policies = list(set(sum(self.policies_dict.values(), [])))
        self.policies_dict = self._discover_policies()

        # Saves the starting state
        self._save_current_elements()

        self.doc

    def _load_models(self):
        # Import pysd here only, because it takes much time to import it
        # and is not used everywhere
        import pysd

        regions = self.GAME_MANAGER.game.REGIONS_DICT.keys()
        self.models = {
            region: pysd.load(self.GAME_MANAGER.game.PYSD_MODEL_FILE)
            for region in regions
        }

        logger.info(
            "Created {} from file {}".format(
                self.models, self.GAME_MANAGER.game.PYSD_MODEL_FILE
            )
        )
        model: pysd.statefuls.Model
        # Initialize each model
        for model in self.models.values():
            # Can set initial conditions to the model variables
            model.set_initial_condition("original")

            # Set the model in run phase
            model.time.stage = "Run"
            logger.debug(f"Model components {model.components}.")
            # cleans the cache of the components
            model.cache.clean()

        self._model = model

    def _discover_policies(self) -> POLICY_DICT:
        """Return a dictionary of the following structure.

        policy_dict = {
            'region0': [
                'policy0', 'policy1', ...
            ],
            'region1': [
                'policy0', ...
            ],
            ...
        }
        Regions can have different policies, which can be useful
        if they run different models.
        """
        return {
            region: [
                name[len(POLICY_PREFIX) :]  # remove policy prefix
                for name in dir(model.components)
                if name.startswith(POLICY_PREFIX)
            ]
            for region, model in self.models.items()
        }

    @property
    def capture_elements(self):
        return self._capture_elements

    @capture_elements.setter
    def capture_elements(self, elements: List[str]):
        """Capture elements are defined the following.

        1. If you assign a list of element, it will be it.
        2. If the capture elements file exists, it will be read.
        3. Else will read from elements_names and process that, and
            create the capture elements file.
        """
        # Check which elements should be captured
        if elements is None:
            elements_file = Path(self.GAME.GAME_DIR, "capture_elements.txt")
            if elements_file.exists():
                with open(elements_file, "r") as f:
                    # Remove the end of line \n
                    elements = [
                        line[:-1] if line[-1] == "\n" else line
                        for line in f.readlines()
                    ]
            else:
                # None captures all elements that are part of the model
                elements = self.elements_names
                for element in elements.copy():
                    # remove the lookup type elements from pysd
                    # as they are just the "table function"
                    if self.doc[element]["Type"] == "lookup":
                        elements.remove(element)
                with open(elements_file, "w") as f:
                    f.writelines("\n".join(elements))
        self._capture_elements = elements
        logger.debug(f"Set captured elements: {elements}")

    def connect(self):
        """Connect the components required by the Model Manager.

        PLOTS_MANAGER is required as it will be called when the
        model has finished a step.
        """
        self.PLOTS_MANAGER = self.GAME_MANAGER.PLOTS_MANAGER

    # endregion Prepare

    # region Actions
    @logger_enter_exit()
    def apply_policies(self):
        """Apply the requested policies to all the requested regions."""
        while not self.GAME_MANAGER.policy_queue.empty():
            # Get the next policy in the queue
            policy = self.GAME_MANAGER.policy_queue.get()
            logger.info(f"apply_policy: {policy}")
            # Access the correct region

            self._apply_policy(policy)

    @logger_enter_exit(level=logging.INFO, with_args=True, ignore_exit=True)
    def _apply_policy(self, policy: Policy):
        """Apply the policy to the model (replacing the function)."""
        model = self.models[policy.region]
        new_method = getattr(model.components, POLICY_PREFIX + policy.name)
        # Removes the prefix and policy name
        method_name = "_".join(policy.name.split("_")[1:])
        # TODO: Apply all the functions corresponding to that policy
        # Now: only apply the one policy
        old_method = getattr(model.components, method_name)
        setattr(model.components, method_name, new_method)

    # endregion Actions

    def read_filepath(self) -> str:
        """Read a user given filepath and return it if exists."""
        filepath = input("Enter filepath of the PySD model you want to use : ")
        if os.path.isfile(filepath):
            return filepath
        else:
            # Prompt again
            print("File not found : ", filepath)
            print("Try again.")
            return self.read_filepath()

    # region Run
    @logger_enter_exit(ignore_exit=True)
    def step(self):
        """Step of the global model.

        Update all regions.
        TODO: Fix that the first step is the same as intialization.
        """
        # Apply the policies
        self.apply_policies()
        # Run each of the models
        self.current_time += self.time_step
        self.current_step += 1

        model: pysd.statefuls.Model
        # Update each region one by one
        for model in self.models.values():
            model._euler_step(self.current_time - model.time())
            model.time.update(self.current_time)
            model.clean_caches()
        # Saves right after the iteration
        self._save_current_elements()
        self.update()

        event = pygame.event.Event(pysimgame.events.ModelStepped, {})
        pygame.event.post(event)

    @logger_enter_exit(ignore_exit=True)
    def _save_current_elements(self):
        for region, model in self.models.items():
            print(model.time(), region)
            self.outputs.at[model.time(), region] = [
                getattr(model.components, key)()
                for key in self.capture_elements
            ]
        # Also save the time
        self.time_axis.append(self.current_time)

    def update(self) -> bool:
        """Each time the update is called is after a step."""
        # Updates the plots, now that the step was done
        # TODO: check if not joining here will lead to an issue
        threading.Thread(
            target=self.PLOTS_MANAGER.update, name="Plot Update"
        ).start()
        # Return true, as only called in step
        return True

    def pause(self):
        """Set the model to pause.

        It can be started again using :py:meth:`run`.
        """
        with Lock():
            self._paused = True
        event = pygame.event.Event(pysimgame.events.Paused, {})
        pygame.event.post(event)
        logger.info("Model paused.")

    def is_paused(self) -> bool:
        """Return True if the game is paused else False."""
        return self._paused

    def run(self):
        """Run the model.

        Will execute a step at each fps.
        It can be paused using :py:meth:`pause`.
        """
        with Lock():
            self._paused = False
        logger.info("Model started.")
        self.clock.tick(self.fps)
        while not self._paused:
            self.step()
            ms = self.clock.tick(self.fps)
            # Record the exectution time
            ms_step = self.clock.get_rawtime()
            logger.info(
                f"Model step executed in {ms_step} ms, ticked {ms} ms."
            )

    def process_events(self, event: pygame.event.Event):
        """Listen the events for this manager."""
        match event:

            case pygame.event.EventType(type=pysimgame.ActionUsed):
                logger.debug(f"Received action {event}")
                if event.region is None:
                    logger.warning(
                        f"No region is selected for action {event.action.name}"
                    )
                else:
                    self.process_action(event.action, event.region)
            case pygame.event.EventType(type=pysimgame.events.SpeedChanged):
                self.fps = event.fps

            case _:
                pass

    @singledispatchmethod
    def process_action(self, action: BaseAction, region: str):
        """Process an action."""
        return NotImplementedType

    @process_action.register
    def _(self, policy: Policy, region: str):
        logger.info(f"processing policy {policy}")
        if policy.activated:
            for model_dependent_method in policy.modifiers:
                # Iterate over all the methods from the modifiers
                model = self[region]
                # NOTE: in pysd we need to set the components of the model object
                attr_name, new_func = model_dependent_method(model.components)
                logger.debug(getattr(model.components, attr_name))
                setattr(model.components, attr_name, new_func)
                logger.debug(getattr(model.components, attr_name))
                logger.debug(f"Setting {attr_name} of {model} to {new_func}")
        else:  # not activated
            logger.warn("Deactivate policy Not implmemented.")

    @process_action.register
    def _(self, action: Edict, region: str):
        logger.info(f"processing Edict {action}")

    @process_action.register
    def _register_budget(self, budget: Budget, region: str):
        # This is sent when the value of the budget is changed
        v = budget.value

        def budget_value():
            return v

        # simply set the function to the models components
        setattr(self[region].components, budget.variable, budget_value)
        logger.debug(f"Set {v} to {budget.variable}.")

    # endregion Run
