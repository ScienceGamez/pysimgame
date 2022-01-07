"""Actions that a player will be able to take during the game.

An Action is a modification of the model performed by the player.
This module contains possible actions that a player will be able to take
during the game.
"""
from __future__ import annotations

import importlib
import inspect
import logging
import pathlib
from abc import abstractmethod
from dataclasses import dataclass, field
from functools import wraps
from importlib.machinery import SourceFileLoader
from sys import path
from types import ModuleType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Tuple,
    TypeVar,
    Union,
)

import pygame
import pysimgame
from pygame.event import Event
from pysimgame.utils import GameComponentManager
from pysimgame.utils.logging import register_logger

if TYPE_CHECKING:
    from pysimgame.model import ModelManager
    from pysimgame.regions_display import RegionComponent
    from pysimgame.types import ModelType

_ACTION_MANAGER: ActionsManager


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
register_logger(logger)


@dataclass(kw_only=True)
class BaseAction:
    """Base class for all actions Classes."""

    name: str
    regions_available: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Executed after the dataclass __init__
        self.register()

    def register(self):
        """Register the method in the Action Manager."""
        dic = _ACTION_MANAGER.actions

        path = _ACTION_MANAGER._current_module
        for mod in path.split("."):
            # Creates dict for having a level organisation
            if mod not in dic:
                dic[mod] = {}

            elif not isinstance(dic[mod], dict):
                logger.error(
                    f"Cannot register {self} because {path} is reserved."
                )
                logger.debug(_ACTION_MANAGER.actions)
            else:
                # Dict already exists
                pass
            # Go deeper in the level
            dic = dic[mod]
        # Finally we put the policy at the correct place
        dic[self.name] = self
        logger.info(f"Registerd {self}")
        logger.debug(_ACTION_MANAGER.actions)

    def deactivate(self):
        """Actual deactivation of the policy."""
        self.activated = False

    def activate(self):
        """Actual activation of the policy."""

        self.activated = True


def modifier_method(
    function: Callable[[ModelType], Tuple[str, Callable[[], float]]],
) -> Callable[..., Tuple[str, Callable[[], float]]]:
    """Decorate all modifiers methods.

    All the modifiers method must return this.

    Does the cancer of this implementation makes it a beauty ?
    Or is it simply the ugliest way of nesting decorators when a better
    solution exists ?
    """

    @wraps(function)
    # Function that is defined here, to help modder create modifiers.
    def modifier_method_wrapper(
        *args, **kwargs
    ) -> Callable[[ModelType], Tuple[str, Callable[[], float]]]:
        # function that will be called in the models manager
        def model_dependent_method(
            model: ModelType,
        ) -> Tuple[str, Callable[[], float]]:
            # Call the docrated function to get attre name and uuser funtion
            attr_name, new_func = function(*args, **kwargs)

            @wraps(new_func)
            # Actual method that will replace the model method
            def model_method() -> float:
                return new_func(model)

            return attr_name, model_method

        return model_dependent_method

    return modifier_method_wrapper


@dataclass(kw_only=True)
class Policy(BaseAction):
    """Represent a set of modifications that will be applied to the model.

    A policy can be activated or deactivated whenever the user wants it.
    """

    modifiers: List[Callable]
    activated: bool = False


@dataclass(kw_only=True)
class Edict(BaseAction):
    """Few step change applied to the model.

    The change disappear at the end of the n_steps.
    """

    n_steps: int = 1


@dataclass(kw_only=True)
class Budget(BaseAction):
    """A budget is a value that can be changed by the user.

    The initial value will be the one of the model.
    Min and max value are either a float or a function if the max and
    mix depend on the model.
    The slider will be updated each step if either the min or max is variable.

    .. note:
        It is your responsability to ensure that max > min.
    """

    variable: str
    min: Union[float, Callable[[ModelType], float]]
    max: Union[float, Callable[[ModelType], float]]
    value: float = 0

    def get_min(self) -> float:
        """Return the min."""
        if callable(self.min):
            return self.min()
        else:
            return self.min

    def get_max(self) -> float:
        """Return the max."""
        if callable(self.max):
            return self.max()
        else:
            return self.max


@modifier_method
def change_constant(
    constant_name: str, value: float
) -> Tuple[str, Callable[[ModelType], float]]:
    """Change the value of the constant."""
    # The function that will actually change the model.
    def new_constant(model):
        return value

    new_constant.__name__ = constant_name
    return (constant_name, new_constant)


@modifier_method
def change_method(
    method_name: str, new_method: Callable
) -> Tuple[str, Callable[[ModelType], float]]:
    """Change a method of the model."""
    return (method_name, new_method)


# Recursive type definition for the Dictonary containing the actions
ActionsDict = Dict[str, Union[BaseAction, "ActionsDict"]]


class ActionsManager(GameComponentManager):
    """The manager for the actions a user can take during the game/simulation."""

    _modules: Dict[str, ModuleType] = {}
    # A tree type of dictionary remebering the actions availables
    actions: ActionsDict = {}

    MODEL_MANAGER: ModelManager

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Register the action manager
        global _ACTION_MANAGER
        _ACTION_MANAGER = self

    def prepare(self):
        """Prepare the action manager by loading all the possible actions.

        Actions are placed in the actions folder of the game.
        Each python file contains different classes and methods.
        """
        actions_dir = pathlib.Path(self.GAME.GAME_DIR, "actions")
        if not actions_dir.exists():
            actions_dir.mkdir()
        actions_files = list(actions_dir.rglob("*.py"))
        logger.debug(f"Files: {actions_files}")

        # TODO: see if we want to add security in the files loaded
        for file in actions_files:
            # Create a special name to not override attributes
            # TODO: make recursive implementation
            module_name = f"user_actions.{file.stem}"
            # Save the current module as Action object register themselfs
            # using it. Note that this would not be thread safe !
            self._current_module = module_name
            module = SourceFileLoader(module_name, str(file)).load_module()
            self._modules[file.stem] = module
        logger.debug(f"Action Mods found : {list(self._modules.keys())}")

    def connect(self):
        self.MODEL_MANAGER = self.GAME_MANAGER.MODEL_MANAGER
        self.REGIONS_MANAGER = self.GAME_MANAGER.REGIONS_MANAGER

    def post_event(self, action: BaseAction):
        """Post an event with the current action.

        This should be used when an action is triggered by the user.
        """

        region = self.REGIONS_MANAGER.selected_region

        if (
            action.regions_available
            and region.name not in action.regions_available
        ):
            # Only some regions and the current region is not in
            self.logger.warn(f"{action} not available for {region}.")
            return

        pygame.event.post(
            Event(pysimgame.ActionUsed, {"action": action, "region": region})
        )
