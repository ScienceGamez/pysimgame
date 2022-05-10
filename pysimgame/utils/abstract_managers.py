"""Contain some abstract managers.

Help to solve some dependency issues with some managers.
"""
from __future__ import annotations
import logging
from pathlib import Path
from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
import pygame


from pygame_gui.ui_manager import UIManager

from pysimgame.utils import register_logger


if TYPE_CHECKING:
    from pysimgame.game import Game
    from pysimgame.game_managers.abstract import AbstractGameManager


class GameComponentManager(ABC):
    """Abstract class for managing different components of the game."""

    GAME_MANAGER: AbstractGameManager
    GAME: Game
    # A logger object for logging purposes
    logger: logging.Logger
    # Optional attribute
    UI_MANAGER: UIManager

    def __init__(self, GAME_MANAGER: AbstractGameManager) -> None:

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

    def process_events(self, event: pygame.event.Event) -> bool:
        """Process events.

        Called in the game manager for listening to the events.

        :param event: _description_
        :return: True if the event was consumed by the manager and
            should not be passed to the following managers.
            Other wise return False.
            If None is return, it is considered as False.
        """
        return False

    def post(self, event: pygame.event.Event | pygame.event.Event.type):
        """Post an event to the pygame event queue.

        Also logs whether the event was correclty send.

        :param event: Either a pygame event, or an event type.
            If an event type is given, this will create an empyt event.
        """
        if not isinstance(event, pygame.event.EventType):
            # Produce event from type
            self.logger.debug(f"Creating an event from event type {event}.")
            event = pygame.event.Event(event)
        self.logger.debug(f"Posting {event}.")
        if not pygame.event.post(event):
            # Unsucessful event post
            self.logger.error(f"{event} was not sent to pygame event queue.")

    def save(self, save_dir: Path):
        """Save component content when the users saves game.

        All the files should be saved in the specified save dir.
        """
        pass

    def load(self, save_dir: Path):
        """Load component content when the users loads game.

        All the files should be loaded from the specified save dir.
        """
        pass

    def quit(self):
        """Quit the game.

        This will be called when the user quits the game.
        """
        pass
