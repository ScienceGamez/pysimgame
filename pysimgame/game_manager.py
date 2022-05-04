"""Contain a class that makes the game management."""
from __future__ import annotations


import json
import os
import pathlib
import sys
import time
from functools import cached_property
from queue import Queue
from threading import Thread
from typing import TYPE_CHECKING, Any, Dict, List, Tuple, Type

import pygame
import pygame.display
import pygame.font
import pygame_gui
from pygame.constants import K_ESCAPE
from pygame.event import Event, EventType
from pygame_gui.ui_manager import UIManager

import pysimgame
from pysimgame.actions.actions import ActionsManager
from pysimgame.actions.gui import ActionsGUIManager
from pysimgame.game import FakeGame, Game
from pysimgame.links.manager import LinksManager
from pysimgame.speed import SpeedManager
from pysimgame.statistics import StatisticsDisplayManager
from pysimgame.utils import logging
from pysimgame.utils.abstract_managers import AbstractGameManager

from .menu import MenuOverlayManager, SettingsMenuManager
from .model import ModelManager, Policy
from .plotting.base import AbstractPlotsManager

from .regions_display import (
    RegionComponent,
    RegionsManager,
    SingleRegionComponent,
)
from .utils.abstract_managers import GameComponentManager
from .utils.directories import (
    GAME_SETTINGS_FILENAME,
    INITIAL_CONDITIONS_FILENAME,
    MODEL_FILENAME,
    PYSDGAME_DIR,
    REGIONS_FILE_NAME,
)
from .utils.logging import PopUpHandler, logger_enter_exit
from .utils.pysimgame_settings import PYSDGAME_SETTINGS, SETTINGS_FILE

if TYPE_CHECKING:
    from .types import ModelType, RegionsDict


BACKGROUND_COLOR = "black"


class GameManager(AbstractGameManager):
    """Main component of the game.

    Organizes the other components managers from the game.
    It is required for the game manager to run on the main thread.
    """

    ## GAME manager MUST be run on a main thread !

    _is_loading: bool = False
    _loading_screen_thread: Thread

    # Components managers
    MANAGERS: Dict[str, GameComponentManager]

    # Set the manager classes this main manager is using
    _manager_classes: List[Type[GameComponentManager]] = [
        RegionsManager,
        MenuOverlayManager,
        ModelManager,
        ActionsGUIManager,
        StatisticsDisplayManager,
        ActionsManager,
        SpeedManager,
        LinksManager,
    ]
    MODEL_MANAGER: ModelManager
    PLOTS_MANAGER: AbstractPlotsManager
    STATISTICS_MANAGER: StatisticsDisplayManager
    ACTIONS_MANAGER: ActionsManager
    REGIONS_MANAGER: RegionsManager
    MENU_OVERLAY: MenuOverlayManager

    POPUP_LOGGER: logging.Logger
    # Stores the time
    CLOCK: pygame.time.Clock

    # Dispaly for rendering everything
    MAIN_DISPLAY: pygame.Surface = None
    RIGHT_PANEL: pygame.Rect
    # Stores the policies waiting to be processed
    policy_queue: Queue[Policy]

    # region Properties

    @property
    def MAIN_DISPLAY(self) -> pygame.Surface:
        main_display = pygame.display.get_surface()
        if main_display is None:
            self.logger.debug("Creating a new display.")
            # Create a new pygame window if we don't know where to render
            main_display = pygame.display.set_mode(
                # First check if they are some specific game settings available
                self.game.SETTINGS.get(
                    "Resolution",
                    # Else check for PYSDGAME or set default
                    PYSDGAME_SETTINGS.get("Resolution", (1080, 720)),
                )
            )
        return main_display

    # endregion
    # region Loading

    def prepare(self):

        # Regions have to be loaded first as they are used by the othres
        self.logger.info("[START] Prepare to start new game.")
        self._is_loading = True
        start_time = time.time()
        # Create the main display (MUST NOT DO THAT IN A THREAD !)
        # (because the display will be cleared at end of thread)
        self.MAIN_DISPLAY
        # TODO: add the theme path
        x, y = size = self.MAIN_DISPLAY.get_size()
        self.UI_MANAGER = UIManager(size)
        self.POPUP_LOGGER = logging.getLogger("PopUps")
        self.POPUP_LOGGER.addHandler(PopUpHandler(self.UI_MANAGER))
        # Split screen in panels
        ratio = 1 / 4
        self.RIGHT_PANEL = pygame.Rect((1 - ratio) * x, 50, ratio * x, y - 50)
        self.LEFT_PANEL = pygame.Rect(0, 0, ratio * x, y)
        # Set the queue for processing of the policies
        self.policy_queue = Queue()

        # Launch a thread for the loading display
        loading_thread = Thread(
            target=self._loading_loop, name="LoadingThread"
        )
        loading_thread.start()

        super().prepare()
        # Assign some specific managers as variable
        # TODO: make this more moddable by using different classes ?
        # Ex. a find ___ manager method
        self.MODEL_MANAGER = self.MANAGERS[ModelManager]
        self.PLOTS_MANAGER = self.MANAGERS[QtPlotManager]
        self.STATISTICS_MANAGER = self.MANAGERS[StatisticsDisplayManager]
        self.ACTIONS_MANAGER = self.MANAGERS[ActionsManager]
        self.REGIONS_MANAGER = self.MANAGERS[RegionsManager]
        self.MENU_OVERLAY = self.MANAGERS[MenuOverlayManager]

        # Model will run on a separated thread
        self.MODEL_THREAD = Thread(
            target=self.MODEL_MANAGER.run, name="ModelThread"
        )

        # Loading is finished (used in the loading screen loop)
        self.logger.debug(f" _is_loading {self._is_loading}")
        self._is_loading = False
        # Display thread is showing the loading screen
        loading_thread.join()
        self.logger.info(
            "[FINISHED] Prepare to start new game. "
            "Loading Time: {} sec.".format(time.time() - start_time)
        )

    @logger_enter_exit()
    def _loading_loop(self):

        self.CLOCK = pygame.time.Clock()
        font = pygame.font.Font("freesansbold.ttf", 32)
        font_surfaces = [
            font.render("Loading .", True, "white"),
            font.render("Loading ..", True, "white"),
            font.render("Loading ...", True, "white"),
        ]

        # Calculate where the loading font should go
        x, y = self.MAIN_DISPLAY.get_size()
        font_position = (x / 2 - font_surfaces[-1].get_size()[1], y / 2)

        self.logger.debug(f"Before loop _is_loading {self._is_loading}")
        counter = 0
        while self._is_loading:
            events = pygame.event.get()
            # Look for quit events
            for event in events:
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                ):
                    self.logger.info("Quitting during loading.")
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.USEREVENT:
                    self.logger.debug(f"User Event : {event}")

            self.MAIN_DISPLAY.fill(BACKGROUND_COLOR)
            self.MAIN_DISPLAY.blit(font_surfaces[counter % 3], font_position)

            pygame.display.update()
            self.CLOCK.tick(1)
            counter += 1

        return self.MAIN_DISPLAY

    # endregion Loading

    def start_new_game(
        self, game: Tuple[Game, str], from_save: pathlib.Path = None
    ):
        """Start a new game."""
        pygame.init()
        self.game = game

        self.logger.info("Preparing the game components")
        self.prepare()

        if from_save:
            self.logger.info(f"Loading from save {from_save}")
            self.load(from_save)
            self.logger.info(f"Save loaded {from_save}")

        self.logger.info("Connecting the game components")
        self.connect()

        self.logger.info("---Game Ready---")

        self.logger.debug(self.MODEL_MANAGER)

        # Start the simulator
        self.MODEL_THREAD.start()
        # Start the game
        self.run_game_loop()

    # region During Game
    def run_game_loop(self):
        """Main game loop.

        TODO: The model, the plot manager and the pygame loop should run
        on separated threads.
        TODO: Use correctly the methods from abstact region component class
        (Note that they will also require proper implementation in the children)
        """
        self.logger.debug(f"[START] run_game_loop")

        while True:
            self.game_loop()
            time_delta = self.CLOCK.tick(self.game.SETTINGS.get("FPS", 20))
            ms = self.CLOCK.get_rawtime()
            self.logger.debug(
                f"Game loop executed in {ms} ms, ticked {time_delta} ms."
            )
            self.draw(time_delta)

    def _start_new_model_thread(self):
        """Start a new thread for the model.

        Used mainly after pausing for restarting.
        """
        # Ensure the thread has ended before restarting
        if self.MODEL_THREAD.is_alive():
            self.logger.warn(f"{self.MODEL_THREAD} is still running.")
            return
        self.MODEL_THREAD.join()

        event = pygame.event.Event(pysimgame.events.UnPaused, {})
        pygame.event.post(event)
        self.MODEL_THREAD = Thread(
            target=self.MODEL_MANAGER.run,
            # Make it a deamon so it stops when the main thread raises error
            daemon=True,
        )
        self.MODEL_THREAD.start()

    def change_model_pause_state(self):
        if self.MODEL_MANAGER.is_paused():
            self._start_new_model_thread()
        else:
            self.MODEL_MANAGER.pause()
        # Space set the game to pause or play

    def _process_textinput_event(self, event) -> bool:
        """Special handling of text input events.

        The event must be a pygame.TEXTINPUT event.
        Convert them into pysimgame events.
        """
        self.logger.setLevel(logging.DEBUG)
        self.logger.debug(f"Processing TextInput.text: {event.text}.")
        match event.text:
            case " ":
                self.logger.debug(f"Found Space")
                self.post(pysimgame.events.TogglePaused)

                self.change_model_pause_state()
                return True

    def draw(self, time_delta: float):
        """Draw the game components on the main display.

        Note that the time delta is required to update pygame_gui's
        managers.
        """
        self.MAIN_DISPLAY.fill(BACKGROUND_COLOR)

        self.REGIONS_MANAGER.update()

        self.UI_MANAGER.update(time_delta / 1000.0)
        for manager in self.MANAGERS.values():
            if hasattr(manager, "UI_MANAGER"):
                # Handles the actions for pygame_gui UIManagers
                manager.UI_MANAGER.update(time_delta / 1000.0)
                manager.UI_MANAGER.draw_ui(self.MAIN_DISPLAY)
            manager.draw()
        self.UI_MANAGER.draw_ui(self.MAIN_DISPLAY)
        pygame.display.update()

    # endregion During Game
    # region Setting Menu
    def start_settings_menu_loop(self):
        """Open the settings menu.

        This requires no computation from the model.
        """

        menu_manager = SettingsMenuManager(self)
        while True:
            self.fps_counter += 1
            time_delta = self.CLOCK.tick(self.game.SETTINGS.get("FPS", 20))
            events = pygame.event.get()
            # Lood for quit events
            for event in events:
                if event.type == pygame.QUIT:

                    pygame.quit()
                    sys.exit()

                menu_manager.process_events(event)

            # Handles the actions for pygame widgets
            menu_manager.update(time_delta - 1000.0)

            self.MAIN_DISPLAY.fill("black")
            menu_manager.draw_ui(self.MAIN_DISPLAY)

            pygame.display.update()

    # endregion Setting Menu
