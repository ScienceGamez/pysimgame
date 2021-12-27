"""Utility module."""
from __future__ import annotations

import logging
import threading
from abc import ABC, abstractmethod
from functools import wraps
from typing import TYPE_CHECKING, Callable, Tuple

import pygame
from pygame_gui.ui_manager import UIManager

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
    # Optional attribute
    UI_MANAGER: UIManager

    def __init__(self, GAME_MANAGER: GameManager) -> None:
        self.GAME_MANAGER = GAME_MANAGER
        self.GAME = GAME_MANAGER.GAME

    def __str__(self) -> str:
        return f"{self.__name__} for '{self.GAME_MANAGER.game.NAME}'"

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
        """Draw the manager."""
        pass

    def process_events(self, event: pygame.event.Event):
        """Called in the game manager for listening to the events."""
        pass

    def update(self) -> bool:
        """Update the manager.

        Meant to be called internally
        when something in the manager is updating.
        Other manager can listen to this using

        :py:meth:`listen_to_update` so they receive the update.

        :return: True if the managers needed an update else false.
        """
        return True

    def listen_to_update(
        self,
        other_manager: GameComponentManager,
        method: Callable,
        threaded: bool = False,
    ) -> None:
        """Add a listener for the update of a certain other manager.

        The method specified will be called after the manager has done
        an update of something internally (update() returns True).

        :param other_manager: The manager to be listened.
        :param method: The method to be called after the update.
        :param threaded: Whether to call the method on a separated thread.
        """
        old_update = other_manager.update

        @wraps(other_manager.update)
        def listened_update():
            if old_update():
                if threaded:
                    threading.Thread(target=method).start()
                else:
                    method()

        other_manager.update = listened_update