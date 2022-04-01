"""The model that runs with the game."""
from __future__ import annotations

import json
import re
from functools import cached_property, singledispatchmethod
from pathlib import Path
from threading import Lock, Thread
from types import NotImplementedType
from typing import TYPE_CHECKING, Callable, Dict, Iterable, List

import pandas as pd
import pygame

import pysimgame
from pysimgame import links
from pysimgame.actions.actions import BaseAction, Budget, Edict, Policy
from pysimgame.links.manager import BaseLink
from pysimgame.links.shared_variables import SharedVariables
from pysimgame.regions_display import RegionComponent
from pysimgame.utils import GameComponentManager

from .utils.logging import logger_enter_exit

if TYPE_CHECKING:
    import pysd

    from pysimgame.types import ExportImportMethod
    from pysimgame.ml.types import TestVariables, TrainVariables

    from .game_manager import GameManager
    from .plotting.manager import PlotsManager
    from .types import POLICY_DICT, ModelMethod, RegionName
    from .ml.manager import MLVarMngr


POLICY_PREFIX = "policy_"
# policy convention
# 1. POLICY_PREFIX
# 2. the name of the policy
# 3. the funciton to replace
# example name: policy_policyname_func_to_replace


class ModelType:
    """Proxy for models.

    Note that you need to implement one of this in your ModelManager.

    Getting Attributes.
    pysimgame will try to call the attributes of your model using
    :py:func:`getattr` in the following way ::

        value = getattr(model_type, '{attr_name}')

    which means that for the valid attributes the current value for
    that attribute should be returned.
    """

    ...


class AbstractModelManager(GameComponentManager):
    """An abstract model manager.

    Provide the minimal API for a model to work.

    A Model in pysimgame is actually composed of one or more regions
    running the same model. This design helps simulating models in
    parallel for optimization, but also allows to generate interaction
    between models, if you want to run simulations with several
    entities that behave the same and have interaction rules.

    In pysdgame, each region correspond to one entity.
    You can run only one region if your model cannot be representated
    by many.

    Each region model is represented by a

    :param models: A dictionary mapping region names
    :param model_lock: A lock for the model. This can be aquired by
        other manager that want to ensure no step can happen while
        they hold the lock.
    """

    models: dict[RegionName, ModelType]
    model_lock: Lock

    def accept_ml_vars_mngr(
        self, ml_manager: MLVarMngr
    ) -> tuple[TrainVariables, TestVariables]:
        """Define the behaviour when ml_manager is listening to this.

        If you don't want your model to be compatible with ML manager,
        don't implement this method, otherwise override it so that it
        return a tuple containing the variable names for x and y.
        """
        raise NotImplementedError(
            f"{type(self).__name__} cannot be used with ML variables."
        )


class ModelManager(AbstractModelManager):
    """Model used to manage the pysd model-s in the simulation.

    Works like a dictionary for the different regions, mapping
    region names to :py:module:`pysd` models of each region.
    It also accepts dictionary of policies where policy apply to
    a model.
    """

    GAME_MANAGER: GameManager
    PLOTS_MANAGER: PlotsManager

    _elements_names: List[str] = None  # Used to internally store elements
    capture_attributes: List[str]
    models: Dict[str, pysd.statefuls.Model]
    _model: pysd.statefuls.Model
    time_step: float
    clock: pygame.time.Clock
    fps: float
    doc: pd.DataFrame

    # Stores some functions that will be called before the step
    _presteps_calls: List[Callable[[], None]] = []

    _export_imports_dic: Dict = {}

    # region Properties
    @property
    def model(self) -> ModelType:
        if not hasattr(self, "_model"):
            self._load_models()

        return self._model.components

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
            # if varname not in self.capture_attributes:
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
                self.logger.warning(
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
        self.logger.debug(f"Doc: {collector}")
        return collector

    @property
    def fps(self):
        """Get the frames per second of the model."""
        return self._fps

    @fps.setter
    def fps(self, new_fps: float):
        if new_fps < 0:
            self.logger.error(f"FPS must be positive not {new_fps}.")
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
            self._elements_names = list(self.model._namespace.values())
            self.logger.debug(
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
        self.capture_attributes = None

        # Create the time managers
        self.clock = pygame.time.Clock()

        self.logger.debug(
            f"initial_time {self._model.components.initial_time()}."
        )
        self.logger.debug(f"time_step {self._model.components.time_step()}.")
        self.logger.debug(f"final_time {self._model.components.final_time()}.")

        self.time_axis = []
        self.current_time = self._model.time()
        self.current_step = int(0)
        self.time_step = self._model.components.time_step()

        self.fps = self.GAME.SETTINGS.get("FPS", 1)

        regions = self.GAME_MANAGER.game.REGIONS_DICT.keys()
        # Create a df to store the output
        index = pd.MultiIndex.from_product(
            [regions, self.capture_attributes],
            names=["regions", "elements"],
        )
        self.logger.debug(f"Created Index {index}")
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

        self.logger.info(
            "Created {} from file {}".format(
                self.models, self.GAME_MANAGER.game.PYSD_MODEL_FILE
            )
        )
        model: pysd.statefuls.Model
        # Initialize each model
        for region, model in self.models.items():
            # Can set initial conditions to the model variables
            if self.GAME.INITIAL_CONDITIONS_FILE.exists():
                # First finds out the constants components
                self._set_initial_conditions(region, model)

            else:
                model.set_initial_condition("original")

            # Set the model in run phase
            model.time.stage = "Run"
            self.logger.debug(f"Model components {model.components}.")
            # cleans the cache of the components
            model.cache.clean()

        self._model = model

    def _set_initial_conditions(
        self, region: RegionName, model: pysd.statefuls.Model
    ):
        # Set the intial conditions of the model
        # The problem is that pysd handles variables differently
        # some variables should not be in the file
        # see new_game.create_initial_conditions_file for that
        # Then we need here to split between constants and
        # other variables
        doc = model.doc()
        constants = list(doc["Py Name"][doc["Type"] == "constant"])

        # Load the conditions for that region
        time, file_conditions = self._load_initial_conditions[region]
        initial_constants, initial_conditions = {}, {}
        # Need to split between constants and others
        for variable, initial_value in file_conditions.items():
            dic_to_use = (
                initial_constants
                if variable in constants
                else initial_conditions
            )
            dic_to_use[variable] = initial_value

        # Set the constants and inital conditions
        self.logger.debug(f"{initial_constants = }  {initial_conditions = }")
        model.set_components(initial_constants)
        model.set_initial_condition((time, initial_conditions))

    @cached_property
    def _load_initial_conditions(self):
        """Load the content form the initial conditions file."""
        with open(self.GAME.INITIAL_CONDITIONS_FILE, "r") as f:
            initial_json = json.load(f)
        initial_conditions = {
            region: (initial_json["_time"], dic)
            for region, dic in initial_json.items()
            if not region == "_time"
        }
        self.logger.debug(f"{initial_conditions = }")
        return initial_conditions

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
    def capture_attributes(self):
        return self._capture_attributes

    @capture_attributes.setter
    def capture_attributes(self, elements: List[str]):
        """Capture elements are defined the following.

        1. If you assign a list of element, it will be it.
        2. If the capture elements file exists, it will be read.
        3. Else will read from elements_names and process that, and
            create the capture elements file.
        """
        # Check which elements should be captured
        if elements is None:
            elements_file = Path(self.GAME.GAME_DIR, "capture_attributes.txt")
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
        self._capture_attributes = elements
        self.logger.debug(f"Set captured elements: {elements}")

    def connect(self):
        """Connect the components required by the Model Manager.

        PLOTS_MANAGER is required as it will be called when the
        model has finished a step.
        """
        self.PLOTS_MANAGER = self.GAME_MANAGER.PLOTS_MANAGER

    # region Links
    @singledispatchmethod
    def process_link(self, link: BaseLink):
        """Process an action."""
        return NotImplementedType

    def link_shared_variables(self, shared_variables: SharedVariables):
        """Link the shared variables in the model.

        .. note:: One of the regions will have its model being 'shared'.
            s.t. the 'shared' variables will be the method of one of the model.
        """
        for var in shared_variables.variables:
            # Finds the method in the 'shared' model
            self._share_method(var)

    def _share_method(self, variable: str):
        """Create the method that is shared by all regions."""

        def _shared_method():
            # This will always call the method called with the variable
            # name, so if it is modified, it will be for all models.
            return getattr(self.model, variable)()

        for model in self.models.values():

            if model.components == self.model:
                # The "shared" model keeps the original method
                continue
            model.set_components({variable: _shared_method})

    def link_region_sum(self, input_variable: str, output_variable: str):
        """Link a region sum variable for the model."""

        def _summed_method():
            _sum = 0
            for model in self.models.values():
                # Adds to the sum
                _sum += getattr(model.components, input_variable)()
            return _sum

        # Add the variable to the models
        setattr(self.model, output_variable, _summed_method)
        # Add it to shared variable
        self._share_method(output_variable)

    def link_modify(
        self, region: RegionName, attribute: str, new_func: ModelMethod
    ):
        """Link that modifies a model single attribute with a new value.

        Connected to the :py:meth:`links.modifiy` method.
        """
        self.models[region].set_components({attribute: new_func})

    def link_region_average(self, input_variable: str, output_variable: str):
        """Link a region average variable for the model."""

        def _average_method():
            _sum = 0
            for model in self.models.values():
                # Adds to the sum
                _sum += getattr(model.components, input_variable)()
            return _sum / len(self.models)

        # Add the variable to the models
        setattr(self.model, output_variable, _average_method)
        # Add it to shared variable
        self._share_method(output_variable)

    def link_export_import(
        self,
        export_variable: str,
        import_variable: str,
        export_import_method: ExportImportMethod,
    ) -> None:
        """Link import export variable to the model.

        :arg export_import_method: The method that should be used to compute the
            export. It takes either 1 or 3 inputs:
                * export_variable
                * import_variable
                * a dict containing the model for each region
            or
                * a dict containing the model for each region
            And returns either a list of float (obtained by looping
            over the models dict and assuming order is preserved)
            or a dictionary specifying the import value for each region.

        .. note:: The model import variable originial function is erased
            so if you need it, consider creating another variable in the
            model.
        """
        # Recall the original methods to not override
        original_methods = {
            region: [
                getattr(model.components, export_variable),
                getattr(model.components, import_variable),
            ]
            for region, model in self.models.items()
        }

        def compute_export_import():

            # Set the original methods before we compute the variable
            for region, methods in original_methods.items():
                model = self.models[region]
                model.set_components(
                    {
                        export_variable: methods[0],
                        import_variable: methods[1],
                    }
                )

            # Compute the actual values
            export_values, import_values = export_import_method(
                {name: model.components for name, model in self.models.items()}
            )
            self.logger.debug(f"{export_values = }")
            self.logger.debug(f"{import_values = }")

            if not isinstance(import_values, dict) or not isinstance(
                export_values, dict
            ):
                self.logger.error(
                    f"Wrong output type for import method:"
                    f" {type(import_values)}. Must be dict."
                )

            for region in self.models.keys():
                self.logger.debug(
                    "Must be the default methods: {}, {}.".format(
                        getattr(
                            self.models[region].components, export_variable
                        )(),
                        getattr(
                            self.models[region].components, import_variable
                        )(),
                    )
                )
                self.models[region].set_components(
                    {
                        export_variable: export_values[region],
                        import_variable: import_values[region],
                    }
                )
                self.logger.debug(
                    "Must be the export import values: {}, {}.".format(
                        getattr(
                            self.models[region].components, export_variable
                        )(),
                        getattr(
                            self.models[region].components, import_variable
                        )(),
                    )
                )

        # The output is computed before every step
        self._presteps_calls.append(compute_export_import)

    # endregion Links
    # endregion Prepare

    # region Run
    @logger_enter_exit(ignore_exit=True)
    def step(self):
        """Step of the global model.

        Update all regions.
        TODO: Fix that the first step is the same as intialization.
        """

        for f in self._presteps_calls:
            f()

        # Update the steps
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

        event = pygame.event.Event(pysimgame.events.ModelStepped, {})
        pygame.event.post(event)

    @logger_enter_exit(ignore_exit=True)
    def _save_current_elements(self):
        for region, model in self.models.items():
            self.outputs.at[model.time(), region] = [
                getattr(model.components, key)()
                for key in self.capture_attributes
            ]
        # Also save the time
        self.time_axis.append(self.current_time)

    def pause(self):
        """Set the model to pause.

        It can be started again using :py:meth:`run`.
        """
        with Lock():
            self._paused = True
        event = pygame.event.Event(pysimgame.events.Paused, {})
        pygame.event.post(event)
        self.logger.info("Model paused.")

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
        self.logger.info("Model started.")
        self.clock.tick(self.fps)
        while not self._paused:
            self.step()
            ms = self.clock.tick(self.fps)
            # Record the exectution time
            ms_step = self.clock.get_rawtime()
            self.logger.info(
                f"Model step executed in {ms_step} ms, ticked {ms} ms."
            )

    def process_events(self, event: pygame.event.Event) -> bool:
        """Listen the events for this manager."""
        match event:
            case pygame.event.EventType(type=pygame.QUIT):
                # Will stop the model thread
                self._paused = True

            case pygame.event.EventType(type=pysimgame.ActionUsed):
                self.logger.debug(f"Received action {event}")
                if event.region is None:
                    self.logger.warning(
                        f"No region is selected for action {event.action.name}"
                    )
                else:
                    self.process_action(event.action, event.region)
            case pygame.event.EventType(type=pysimgame.events.SpeedChanged):
                self.fps = event.fps

            case _:
                pass

    # region Actions

    @singledispatchmethod
    def process_action(self, action: BaseAction, region: str):
        """Process an action."""
        return NotImplementedType

    @process_action.register
    def _(self, policy: Policy, region: str):
        self.logger.info(f"processing policy: {policy.name}")
        model: pysd.statefuls.Model = self[region]
        if policy.activated:
            for model_dependent_method in policy.modifiers:
                # Iterate over all the methods from the modifiers

                # NOTE: in pysd we need to set the components of the model object
                attr_name, new_func = model_dependent_method(model.components)

                # Stores in the policy the original methods
                policy.original_methods[attr_name] = getattr(
                    model.components, attr_name
                )
                self.logger.debug(getattr(model.components, attr_name))
                model.set_components({attr_name: new_func})
                # setattr(model.components, attr_name, new_func)
                self.logger.debug(getattr(model.components, attr_name))
                self.logger.debug(
                    f"Setting {attr_name} of {model} to {new_func}"
                )
        else:  # not activated
            self.logger.debug(f"Deactivating {policy.name}.")
            # Restore the original methods
            model.set_components(policy.original_methods)

    @process_action.register
    def _(self, action: Edict, region: str):
        self.logger.info(f"processing Edict {action}")

    @process_action.register
    def _register_budget(self, budget: Budget, region: str):
        # This is sent when the value of the budget is changed
        v = budget.value

        def budget_value():
            return v

        # simply set the function to the models components
        setattr(self[region].components, budget.variable, budget_value)
        self.logger.debug(f"Set {v} to {budget.variable}.")

    # endregion Actions
    # endregion Run
