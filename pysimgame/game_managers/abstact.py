from __future__ import annotations
import concurrent.futures
import logging
from pathlib import Path
import sys
from typing import TYPE_CHECKING, Type


from pysimgame.game import Game
from pysimgame.utils.abstract_managers import GameComponentManager

if TYPE_CHECKING:
    import pygame
    from pygame.event import Event, EventType

    from pysimgame.actions.actions import ActionsManager
    from pysimgame.menu import MenuOverlayManager
    from pysimgame.model import ModelManager
    from pysimgame.plotting.base import AbstractPlotsManager
    from pysimgame.regions_display import RegionsManager
    from pysimgame.statistics import StatisticsDisplayManager

_GAME_MANAGER: AbstractGameManager = None


class AbstractGameManager(GameComponentManager):
    """An abstract game manager that contain the minimum required.

    All game managers should inherit from this one.
    The main idea is that only the
    :py:attr`_manager_classes` should be replaced by the components.
    """

    # Different game things
    _game: Game
    _model_fps: float = 1
    fps_counter: int = 0

    # Components managers
    MANAGERS: dict[str, GameComponentManager]

    # Set the manager classes this main manager is using
    _manager_classes: list[Type[GameComponentManager]]

    # Mandatory managers
    MODEL_MANAGER: ModelManager
    PLOTS_MANAGER: AbstractPlotsManager
    STATISTICS_MANAGER: StatisticsDisplayManager
    ACTIONS_MANAGER: ActionsManager
    REGIONS_MANAGER: RegionsManager
    MENU_OVERLAY: MenuOverlayManager

    # Stores the time
    CLOCK: pygame.time.Clock

    GAME: Game

    @property
    def GAME(self) -> Game:
        """A :py:class:`Game` instance for the current game managed."""
        return self._game

    @property
    def game(self) -> Game:
        """A :py:class:`Game` instance for the current game managed."""
        return self._game

    @game.setter
    def game(self, game: tuple[Game, str]):
        if isinstance(game, str):
            # Creates the game object required
            game = Game(game)
        self._game = game
        self.logger.info(f"New game set: '{self.game.NAME}'.")

    def __init__(self) -> None:
        """Override the main :py:class:`GameManager` is the main organizer."""
        self._set_logger()
        global _GAME_MANAGER
        if _GAME_MANAGER is None:
            _GAME_MANAGER = self
        self.MANAGERS = {}

    def game_loop(self):
        """Run one tick of the game loop."""
        self.logger.debug(f"[START] iteration of run_game_loop")
        self.fps_counter += 1
        events = pygame.event.get()
        self.logger.debug(f"Events: {events}")
        # Lood for quit events
        for event in events:
            self.process_event(event)

    def prepare(self):
        """Prepare the different managers."""

        def start_manager(manager_class: Type[GameComponentManager]):
            """Start a game manager component.

            Call the prepare method, that is not dependent on other component.
            """
            manager = manager_class(self)
            manager.prepare()
            return manager

        # We lauch threads here
        # At the moment it is not very efficient as all is loaded from
        # local ressource but in the future we might want to have some
        # networking processes to download some content.
        with concurrent.futures.ThreadPoolExecutor(
            thread_name_prefix="ManagerPrepare"
        ) as executor:

            future_to_manager = {
                executor.submit(start_manager, manager_class): manager_class
                for manager_class in self._manager_classes
            }
            # Wait for the threads to finish
            for future in concurrent.futures.as_completed(future_to_manager):
                manager_class = future_to_manager[future]
                try:
                    manager = future.result()
                except Exception as exc:
                    raise Exception(
                        f"Could not prepare {manager_class}."
                    ) from exc
                else:
                    self.MANAGERS[manager_class] = manager

        self.logger.debug(f"MANAGERS : {self.MANAGERS}")

    def process_event(self, event: Event):
        self.logger.debug(f"Processing {event}")
        self.UI_MANAGER.process_events(event)
        match event:
            case EventType(type=pygame.QUIT):
                self._managers_process_event(event)
                pygame.quit()
                sys.exit()
            case EventType(type=pygame.TEXTINPUT):
                if self._process_textinput_event(event):
                    # Consumed event
                    return
            case EventType(type=pygame.KEYDOWN):
                # NOTE: Only handle events that are not already handled
                # by pygame.TEXTINPUT events
                if self._process_keydown_event(event):
                    # Consumed event
                    return

        self._managers_process_event(event)

    def _process_keydown_event(self, event) -> bool:
        """Process key down events.

        Should only process events that are not already processed in
        :py:meth:`_process_textinput_event` .
        """
        match event.key:
            case pygame.K_ESCAPE:
                self.post(pygame.QUIT)

    def _managers_process_event(self, event):
        for manager in self.MANAGERS.values():
            if manager.process_events(event):
                # Consumed event are blocked for other managers
                return

    def connect(self):
        # Components are ready, we can connect them together
        for manager in self.MANAGERS.values():
            manager.connect()

    def run_game_loop(self):
        ...

    def load(self, save_file: Path):
        """Load a game from the save.

        TODO: Implement
        Idea: make every manager save in a file what they need and then
        compress into a file.
        """
        save_dir = save_file.parent
        for manager in self.MANAGERS.values():
            manager.load(save_dir)
