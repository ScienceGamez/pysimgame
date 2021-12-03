"""The model that runs with the game."""
from __future__ import annotations
from functools import cached_property
import logging
import os
import shutil
from dataclasses import dataclass
from threading import Lock, Thread
import threading

from typing import Dict, Iterable, List
import pandas as pd


from typing import TYPE_CHECKING

import pygame


from pysdgame.regions_display import RegionComponent
from pysdgame.utils import GameComponentManager

from .utils.logging import logger, logger_enter_exit

if TYPE_CHECKING:
    from pysdgame.game_manager import GameManager
    from pysdgame.plots import PlotsManager
    import pysd


POLICY_PREFIX = "policy_"
# policy convention
# 1. POLICY_PREFIX
# 2. the name of the policy
# 3. the funciton to replace
# example name: policy_policyname_func_to_replace
POLICY_DICT = Dict[str, List[str]]


@dataclass
class Policy:
    """Represent a policy chosen by the user attributed to a region."""

    name: str
    region: RegionComponent


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
    time_step: float
    clock: pygame.time.Clock
    fps: float

    def __init__(self, GAME_MANAGER: GameManager) -> None:
        super().__init__(GAME_MANAGER)

    def prepare(self):

        self.GAME_MANAGER = self.GAME_MANAGER
        self._load_models()
        # Set the captured_elements
        self.capture_elements = None

        # Create the time managers
        self.clock = pygame.time.Clock()
        model = list(self.models.values())[0]  # Get the first model
        logger.debug(f"initial_time {model.components.initial_time()}.")
        logger.debug(f"time_step {model.components.time_step()}.")
        logger.debug(f"final_time {model.components.final_time()}.")

        self.time_axis = []
        self.current_time = model.time()
        self.current_step = int(0)
        self.time_step = model.components.time_step()

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

    @property
    def fps(self):
        """Get the frames per second of the model."""
        return self._fps

    @fps.setter
    def fps(self, new_fps: float):
        if new_fps < 0:
            raise ValueError(f"FPS must be positive not {new_fps}.")
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

    def __getitem__(self, key):
        return self.models[key]

    def time(self):
        """Return the current time."""
        raise NotImplementedError("Should be pointing to the submodel time.")

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
        # Check which elements should be captured
        if elements is None:
            # None captures all elements that are part of the model
            elements = self.elements_names
        self._capture_elements = elements
        logger.info(f"Set captured elements: {elements}")

    def connect(self):
        """Connect the components required by the Model Manager.

        PLOTS_MANAGER is required as it will be called when the
        model has finished a step.
        """
        self.PLOTS_MANAGER = self.GAME_MANAGER.PLOTS_MANAGER

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

    @logger_enter_exit(ignore_exit=True)
    def _save_current_elements(self):
        for region, model in self.models.items():
            self.outputs.at[model.time(), region] = [
                getattr(model.components, key)()
                for key in self.capture_elements
            ]
        # Also save the time
        self.time_axis.append(self.current_time)

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
