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
from typing import TYPE_CHECKING, Any, Callable, Dict, List

from pysdgame.utils import GameComponentManager
from pysdgame.utils.logging import register_logger

if TYPE_CHECKING:
    from pysdgame.regions_display import RegionComponent

_ACTION_MANAGER: ActionsManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
register_logger(logger)


@dataclass(kw_only=True)
class BaseAction:
    """Base class for all actions Classes."""

    name: str

    def __post_init__(self) -> None:
        # Executed after the dataclass __init__
        self.register()

    @abstractmethod
    def register(self):
        """Register the method in the Action Manager."""
        ...


def action_method(function: Callable):
    """Decorator for all actions methods."""

    @wraps(function)
    def wrapped(*args, **kwargs):
        return function(*args, **kwargs)

    return wrapped


@dataclass(kw_only=True)
class Policy(BaseAction):
    """Represent a set of actions that will be replaced."""

    actions: List[Callable]
    regions_available: List[str] = field(default_factory=list)

    def register(self):
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


@action_method
def change_constant(constant_name: str, value: float):
    """Change the value of the constant."""

    def new_constant(model):
        """The function that will actually change the model."""
        return value

    new_constant.__name__ = constant_name
    return (constant_name, new_constant)


@action_method
def change_method(method_name: str, new_method: Callable):
    """Change a method of the model."""
    return (method_name, new_method)


class ActionsManager(GameComponentManager):
    _modules: Dict[str, ModuleType] = {}
    # A tree type of dictionary remebering the actions availables
    actions: Dict[str, Any] = {}

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
        pass
