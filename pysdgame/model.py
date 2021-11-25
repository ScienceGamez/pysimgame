"""The model that runs with the game."""
from __future__ import annotations
from functools import cached_property
import os
import shutil

from typing import Dict, Iterable, List
import numpy as np
import pandas as pd


from typing import TYPE_CHECKING

from .utils.logging import logger

if TYPE_CHECKING:
    from pysdgame.game_manager import GameManager


POLICY_PREFIX = "policy_"
# policy convention
# 1. POLICY_PREFIX
# 2. the name of the policy
# 3. the funciton to replace
# example name: policy_policyname_func_to_replace
POLICY_DICT = Dict[str, List[str]]


class ModelManager:
    """Model used to manage the pysd model-s in the simulation.

    Works like a dictionary for the different regions, mapping
    region names to :py:module:`pysd` models of each region.
    It also accepts dictionary of policies where policy apply to
    a model.
    """

    game_manager: GameManager
    _elements_names: List[str] = None  # Used to internally store elements

    def __init__(
        self,
        game_manager: GameManager,
        capture_elements: List[str] = None,
    ) -> None:
        """Create a model manager.

        Attributes:
            regions: name of the simuualtion regions
            capture_elements: The elements that will be returned by
                :py:meth:`get_current_data`. If None, will return all
                what is available.
        """
        # Import pysd here only, because it takes much time to import it
        import pysd

        self.game_manager = game_manager
        regions = game_manager.game.REGIONS_DICT.keys()
        self.models = {
            region: pysd.load(game_manager.game.PYSD_MODEL_FILE)
            for region in regions
        }

        logger.info(
            "Created {} from file {}".format(
                self.models, game_manager.game.PYSD_MODEL_FILE
            )
        )

        # Initialize each model
        for model in self.models.values():
            # Can set initial conditions to the model variables
            model.set_initial_condition("original")

            # Set the model in run phase
            model.time.stage = "Run"
            # cleans the cache of the components
            logger.debug(f"Model components {model.components}.")
            model.cache.clean()

        self.time = model.time

        # Create the axis of timesteps
        logger.debug(f"initial_time {model.components.initial_time()}.")
        logger.debug(f"time_step {model.components.time_step()}.")
        logger.debug(f"final_time {model.components.final_time()}.")
        self.time_axis = np.arange(
            model.time(),
            model.components.final_time() + model.components.time_step(),
            step=model.components.time_step(),
            dtype=float,
        )
        logger.debug(f"Built time array: {self.time_axis}.")
        self.t_serie = iter(self.time_axis)
        self.current_time = model.time()
        self.current_step = int(0)

        self.capture_elements = capture_elements

        # Create a df to store the output
        index = pd.MultiIndex.from_product(
            [regions, self.capture_elements],
            names=["regions", "elements"],
        )
        logger.debug(f"Created Index {index}")
        self.outputs = pd.DataFrame(columns=index)
        # Sort the indexes for performance
        self.outputs.sort_index()

        # Saves the starting state
        self._save_current_elements()

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

    def apply_policies(self, policies: POLICY_DICT):
        """Apply the requested policies to all the requested regions."""
        for region, policies in policies.items():
            # Access the correct region
            model = self.models[region]
            for policy in policies:
                self._apply_policy(model, policy)

    def _apply_policy(self, model, policy: str):
        """Apply the policy to the model (replacing the function)."""
        new_method = getattr(model.components, POLICY_PREFIX + policy)
        # Removes the prefix and policy name
        method_name = "_".join(policy.split("_")[1:])
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

    def _save_current_elements(self):
        logger.debug(f"[STARTED]_save_current_elements : {self.outputs}")
        for region, model in self.models.items():
            self.outputs.at[model.time(), region] = [
                getattr(model.components, key)()
                for key in self.capture_elements
            ]
        logger.debug(f"[FINISHED]_save_current_elements : {self.outputs}")

    def step(self):
        """Step of the global model.

        Update all regions.
        TODO: Fix that the first step is the same as intialization.
        """
        # Run each of the models
        self.current_time = next(self.t_serie)
        self.current_step += 1
        # Update each region one by one
        for model in self.models.values():
            model._euler_step(self.current_time - model.time())
            model.time.update(
                self.current_time
            )  # this will clear the stepwise caches
            model.components.cache.reset(self.current_time)
        # Saves right after the iteration
        self._save_current_elements()

    def get_current_data(self):
        return self.outputs.loc[self.time()]
