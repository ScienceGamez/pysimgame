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
import pysdgame
from pygame.event import Event
from pysdgame.utils import GameComponentManager
from pysdgame.utils.logging import register_logger

if TYPE_CHECKING:
    from pysdgame.model import ModelManager
    from pysdgame.regions_display import RegionComponent
    from pysdgame.types import ModelType

_ACTION_MANAGER: ActionsManager


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
register_logger(logger)


@dataclass(kw_only=True)
class BaseAction:
    """Base class for all actions Classes."""

    name: str
    actions: List[Callable]
    regions_available: List[str] = field(default_factory=list)
    activated: bool = False

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


def action_method(
    function: Callable[ModelType, float],
) -> Callable[..., Tuple[str, Callable[[], float]]]:
    """Decorator for all actions methods.

    All the actions method must return this.

    Does the cancer of this implementation makes it a beauty ?
    Or is it simply the ugliest way of nesting decorators when a better
    solution exists ?
    """
    # Function that is defined here, to help modder create actions.
    @wraps(function)
    def action_method_wrapper(*args, **kwargs):
        # function that will be called in the model manager
        def model_dependent_method(model):
            # Call the docrated function to get attre name and uuser funtion
            attr_name, new_func = function(*args, **kwargs)
            # Actual method that will replace the model method
            @wraps(new_func)
            def model_method():
                return new_func(model)

            return attr_name, model_method

        return model_dependent_method

    return action_method_wrapper


@dataclass(kw_only=True)
class Policy(BaseAction):
    """Represent a set of modifications that will be applied to the model.

    A policy can be activated or deactivated whenever the user wants it.
    """


@dataclass(kw_only=True)
class Trigger(BaseAction):
    """Few step change applied to the model.

    The change disappear at the end of the n_steps.
    """

    n_steps: int = 1


@dataclass(kw_only=True)
class Budget(BaseAction):
    """A budget is a value that can be change by the user."""

    min: float
    max: float


@action_method
def change_constant(
    constant_name: str, value: float
) -> Tuple[str, Callable[ModelType, float]]:
    """Change the value of the constant."""
    # The function that will actually change the model.
    def new_constant(model):
        return value

    new_constant.__name__ = constant_name
    return (constant_name, new_constant)


@action_method
def change_method(
    method_name: str, new_method: Callable
) -> Tuple[str, Callable[ModelType, float]]:
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
        actions_files = list(actions_dir.rglob("*.py"))
        logger.debug(f"Files: {actions_files}")
        # TODO: see if we want to add security in the files loaded
        for file in actions_files:
            # Create a special name to not override attributes
            module_name = f"user_actions.{file.stem}"
            # Save the current module as Action object register themselfs
            # using it. Note that this would not be thread safe !
            self._current_module = module_name
            module = SourceFileLoader(module_name, str(file)).load_module()
            self._modules[file.stem] = module
        logger.debug(f"Action Mods found : {list(self._modules.keys())}")

    def connect(self):
        self.MODEL_MANAGER = self.GAME_MANAGER.MODEL_MANAGER

    def trigger(self, action: BaseAction):
        """Trigger the action."""
