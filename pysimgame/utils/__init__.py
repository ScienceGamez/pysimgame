"""Utility module."""
from __future__ import annotations

import pathlib
import threading
from abc import ABC, abstractmethod
from functools import wraps
from typing import TYPE_CHECKING, Callable, Tuple

import pygame
from pygame_gui.ui_manager import UIManager

from .logging import logging, register_logger

if TYPE_CHECKING:
    from pysimgame.game_manager import Game, GameManager


def recursive_dict_missing_values(dic_from: dict, dic_to: dict) -> dict:
    """Assign missing values from a dictonary to another.

    Assignement happens in place
    """
    for key, value in dic_from.items():
        if key not in dic_to:
            dic_to[key] = value
        elif isinstance(value, dict):
            dic_to[key] = recursive_dict_missing_values(
                dic_from[key], dic_to[key]
            )
        else:
            pass
    return dic_to


def close_points(
    point1: Tuple[int, int], point2: Tuple[int, int], PIXEL_THRESHOLD: int = 10
) -> bool:
    """Return True if the points are close enough else False.

    Use Manatthan distance.
    """
    return (
        abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])
        < PIXEL_THRESHOLD
    )


class _HintDisplay:
    """Display hints for the user on his screen.

    Currently only prints in terminal but could put things on screen
    in the future.
    """

    def __main__(self):
        """Create the hint displayer."""
        # TODO implement this to have proper on screan display
        logger = logging.getLogger(__name__)
        pass

    def show(self, text: str):
        """Show the text as hint."""
        print(text)


HINT_DISPLAY = _HintDisplay()


class GameComponentManager(ABC):
    """Abstract class for managing different components of the game."""

    GAME_MANAGER: GameManager
    GAME: Game
    # A logger object for logging purposes
    logger: logging.Logger
    # Optional attribute
    UI_MANAGER: UIManager

    def __init__(self, GAME_MANAGER: GameManager) -> None:

        self.GAME_MANAGER = GAME_MANAGER
        self.GAME = GAME_MANAGER.GAME

        self._set_logger()

    def _set_logger(self):
        # Create the logger with the name of the component
        self.logger = logging.getLogger(type(self).__name__)
        register_logger(self.logger)

    def __str__(self) -> str:
        return f"{type(self).__name__} for {self.GAME_MANAGER.game.NAME}"

    @abstractmethod
    def prepare(self):
        """Prepare the component to be ready.

        This part should load content required and instantiate anything.
        Note that this method should be able to be called on a dedicated thread.
        """
        return NotImplemented

    @abstractmethod
    def connect(self):
        """Connect this component manager to the other components.

        Will be automatically called by the :py:class:`GameManager`.
        This will be called on the main thread.
        """
        return NotImplemented

    def draw(self):
        """Draw the manager (optional).

        Optional. Only implement if you want to draw something on the
        screen. Drawing order depends on the order set of the managers
        inside the GameManager.
        If you have set a UI_MANAGER inside you component manager,
        you don't need to call its update method here, as it is
        automatically called from the GameManager.
        """
        pass

    def process_events(self, event: pygame.event.Event):
        """Called in the game manager for listening to the events."""
        pass

    def save(self, save_dir: pathlib.Path):
        """Save component content when the users saves game.

        All the files should be saved in the specified save dir.
        """
        pass

    def load(self, save_dir: pathlib.Path):
        """Load component content when the users loads game.

        All the files should be loaded from the specified save dir.
        """
        pass

    def quit(self):
        """Quit the game.

        This will be called when the user quits the game.
        """
        pass


def create_modding_file(game: Game | str):
    """Create the modding helper file."""
    import json

    if isinstance(game, str):
        from pysimgame.game_manager import Game

        game = Game(game)
    file = pathlib.Path(game.GAME_DIR, "modding_help.json")

    dic = {
        "Regions": [k for k in game.REGIONS_DICT.keys()],
        "Attributes": [m for m in game.load_model()._namespace.values()],
    }

    with file.open("w") as f:
        json.dump(dic, f, indent=2)
