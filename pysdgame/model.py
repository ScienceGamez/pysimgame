"""The model that runs with the game."""
import os

from typing import Dict, List
import numpy as np
import pandas as pd
import pysd


POLICY_PREFIX = 'policy_'
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

    def __init__(
        self,
        regions: List[str],
        capture_elements: List[str],
        final_time: float = 2600,
        d_T: float = 0.5,
    ) -> None:
        """Create a illuminati model.

        Attributes:
            regions: name of the simuualtion regions
            capture_elements: The elements that will be returned by
                :py:meth:`get_current_data`.
        """
        regions = regions.copy()
        self.models = {
            region: pysd.load(self.pysd_model_file())
            for region in regions
        }

        # Initialize each model
        for model in self.models.values():
            # Can set initial conditions to the model variables
            model.set_initial_condition('original')

            # Set the model in run phase
            model.time.stage = 'Run'
            # cleans the cache of the components
            model.components.cache.clean()

        self.time = model.time

        # Create the axis of timesteps
        self.t_serie = iter(np.arange(
            model.time(),
            final_time,
            step=d_T, dtype=float
        ))
        self.current_time = model.time()
        self.current_step = int(0)

        # Create a df to store the output
        index = pd.MultiIndex.from_product([regions, capture_elements])
        self.outputs = pd.DataFrame(columns=index)

        self.capture_elements = capture_elements
        # Saves the starting state
        self._save_current_elements()

    def __getitem__(self, key):
        return self.models[key]

    def time(self):
        """Return the current time."""
        raise NotImplementedError('Should be pointing to the submodel time.')

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
                name[len(POLICY_PREFIX):]  # remove policy prefix
                for name in dir(model.components)
                if name.startswith(POLICY_PREFIX)
            ] for region, model in self.models.items()
        }

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
        method_name = '_'.join(policy.split('_')[1:])
        # TODO: Apply all the functions corresponding to that policy
        # Now: only apply the one policy
        old_method = getattr(model.components, method_name)
        setattr(model.components, method_name, new_method)


    def pysd_model_file(self) -> str:
        """Load the file name of the pysd simulation."""
        return os.path.join('..', 'Vensim', 'WRLD3-03', 'WRLD3-Ills-fate.py')

    def _save_current_elements(self):
        for region, model in self.models.items():
            self.outputs.at[model.time(), region] = [
                getattr(model.components, key)()
                for key in self.capture_elements
            ]

    def step(self):
        """Step of the Illuminati model.

        Update all regions.
        TODO: Fix that the first step is the same as intialization.
        """
        # Run each of the models
        self.current_time = next(self.t_serie)
        self.current_step += 1
        # Update each region one by one
        for model in self.models.values():
            model._euler_step(self.current_time - model.time())
            model.time.update(self.current_time)  # this will clear the stepwise caches
            model.components.cache.reset(self.current_time)
        # Saves right after the iteration
        self._save_current_elements()

    def get_current_data(self):
        return self.outputs.loc[self.time()]
