"""Contain a class that makes the game management."""
from __future__ import annotations

import os
import pathlib
import sys
import json
import time
from threading import Thread
from queue import Queue
from functools import cached_property
from typing import Any, Dict, Tuple
import pygame
import pygame.display
from pygame.event import Event
import pygame.font
import pygame_gui
from pygame_gui.ui_manager import UIManager

from pysdgame.statistics import StatisticsDisplayManager

from .utils.pysdgame_settings import PYSDGAME_SETTINGS, SETTINGS_FILE
from .types import RegionsDict
from .menu import MenuOverlayManager, SettingsMenuManager
from .utils import GameComponentManager, recursive_dict_missing_values
from .plots import PlotsManager
from .regions_display import (
    RegionComponent,
    RegionsSurface,
    SingleRegionComponent,
)
from .model import ModelManager, Policy
from .utils.logging import logger, logger_enter_exit

from .utils.directories import (
    GAME_SETTINGS_FILENAME,
    MODEL_FILENAME,
    PYSDGAME_DIR,
    REGIONS_FILE_NAME,
)


class Game:
    """Helper class representing a game type from pysd.

    Holds meta information on a game.
    Games all have a model they are based on and a set of settings to
    define how they should be played.
    """

    NAME: str
    GAME_DIR: pathlib.Path
    REGIONS_FILE: pathlib.Path
    PYSD_MODEL_FILE: pathlib.Path

    REGIONS_DICT: RegionsDict

    def __init__(self, name: str, create: bool = False) -> None:
        self.NAME = name
        self.GAME_DIR = pathlib.Path(PYSDGAME_DIR, name)
        match self.GAME_DIR.exists(), create:
            case False, True:  # Game creation
                self.GAME_DIR.mkdir()
            case False, False:  # Reading a non existing game
                raise RuntimeError(f"Game '{name}' cannot be found.")
        self.REGIONS_FILE = pathlib.Path(self.GAME_DIR, REGIONS_FILE_NAME)
        self.PYSD_MODEL_FILE = pathlib.Path(self.GAME_DIR, MODEL_FILENAME)
        self._SETTINGS_FILE = pathlib.Path(
            self.GAME_DIR, GAME_SETTINGS_FILENAME
        )

    @cached_property
    def REGIONS_DICT(self) -> RegionsDict:
        """Load the dictionary of the regions for that game."""
        with open(self.REGIONS_FILE, "r") as f:
            dic = json.load(f)
        logger.info("Region file loaded.")
        logger.debug(f"Region file content: {dic}.")

        return (
            {  # Load regions from what is in the file
                region_dict["name"]: RegionComponent.from_dict(region_dict)
                for region_dict in dic.values()
            }
            if len(dic) != 0
            # Load a single region if they are not in the file
            else {"": SingleRegionComponent()}
        )

    @cached_property
    def SETTINGS(self) -> Dict[str, Any]:
        """Load the settings of the game."""

        with open(self._SETTINGS_FILE, "r") as f:
            settings = json.load(f)
        # Check everything necessary is in settings, else add
        if "Themes" not in settings:
            settings["Themes"] = {}
        logger.info("Game Settings loaded.")
        logger.debug(f"Game Settings content: {settings}.")
        return settings

    def save_settings(self) -> None:
        """Save the game settings.

        Settings can be modified directly by calling Game.SETTINGS .
        The settings will only be saved using this method.
        """

        with open(self._SETTINGS_FILE, "w") as f:
            json.dump(f, self.SETTINGS)
        logger.info("Game Settings saved.")
        logger.debug(f"Game Settings content: {self.SETTINGS}.")


class GameManager(GameComponentManager):
    """Main component of the game.

    Organizes the other components from the game.
    """

    ## GAME manager MUST be run on a main thread !
    _game: Game
    _model_fps: float = 1
    fps_counter: int = 0
    MODEL_MANAGER: ModelManager = None
    _is_loading: bool = False
    _loading_screen_thread: Thread
    UI_MANAGER: UIManager
    PLOTS_MANAGER: PlotsManager
    STATISTICS_MANAGER: StatisticsDisplayManager
    # Stores the time
    CLOCK: pygame.time.Clock

    # Dispaly for rendering everything
    MAIN_DISPLAY: pygame.Surface = None
    # Stores the policies waiting to be processed
    policy_queue: Queue[Policy]

    def __init__(self) -> None:
        """Override the main :py:class:`GameManager` is the main organizer."""
        pass

    # region Properties
    @property
    def GAME(self) -> Game:
        """A :py:class:`Game` instance for the current game managed."""
        return self._game

    @property
    def game(self) -> Game:
        """A :py:class:`Game` instance for the current game managed."""
        return self._game

    @game.setter
    def game(self, game: Tuple[Game, str]):
        if isinstance(game, str):
            # Creates the game object required
            game = Game(game)
        self._game = game
        logger.info(f"New game set: '{self.game.NAME}'.")

    @property
    def MAIN_DISPLAY(self) -> pygame.Surface:
        main_display = pygame.display.get_surface()
        if main_display is None:
            logger.debug("Creating a new display.")
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
    def _load_game_content(self):
        logger.debug(f"[START] Loading {self.game.NAME}.")
        # This will load the settings
        self.game.SETTINGS
        logger.debug(f"[FINISHED] Loading {self.game.NAME}.")

    @logger_enter_exit()
    def _create_display(self):

        self._loading_screen_thread = Thread(target=self._loading_loop)
        self._loading_screen_thread.start()

        # Set up a pygame_gui manager
        # TODO: add the theme path
        self.UI_MANAGER = UIManager(self.MAIN_DISPLAY.get_size())

        self._prepare_regions_display()
        self._prepare_graph_display()
        self._prepare_menu_displays()

        self._loading_screen_thread.join()

    def _prepare_regions_display(self):
        self.REGIONS_DISPLAY = RegionsSurface(self)

    def _prepare_menu_displays(self):
        """Set up the menu displayer of the game.

        Menu buttons are set at the top right.
        """
        self.MENU_OVERLAY = MenuOverlayManager(self)
        self.MENU_OVERLAY.prepare()

    def _prepare_graph_display(self):
        self.PLOTS_MANAGER = PlotsManager(self)
        self.PLOTS_MANAGER.prepare()
        # self.PLOTS_MANAGER.add_graph()

    def _start_model(self):
        logger.debug("[START] Starting the model")

        # Create an instance managing the model
        self.MODEL_MANAGER = ModelManager(self)
        self.MODEL_MANAGER.prepare()

        self.MODEL_THREAD = Thread(target=self.MODEL_MANAGER.run)

        logger.debug("[FINISHED] Starting the model")
        # await asyncio.sleep(1)
        return

    def _prepare_stats(self):
        self.STATISTICS_MANAGER = StatisticsDisplayManager(self)
        self.STATISTICS_MANAGER.prepare()
        return

    def prepare(self):
        self._prepare_components()

    def _prepare_components(self):
        # Regions have to be loaded first as they are used by the othres
        logger.info("[START] Prepare to start new game.")
        self._is_loading = True
        start_time = time.time()
        # Create the main display (MUST NOT DO THAT IN A THREAD !)
        # (because the display will be cleared at end of thread)
        self.MAIN_DISPLAY

        # Set the queue for processing of the policies
        self.policy_queue = Queue()

        # We lauch threads here
        # At the moment it is not very efficient as all is loaded from
        # local ressource but in the future we might want to have some
        # networking processes to download some content.

        p0 = Thread(target=self._start_model, name="Starting Model Manager")
        p0.start()
        p1 = Thread(
            target=self._load_game_content, name="Game Content Loading"
        )
        p1.start()
        display_thread = Thread(
            target=self._create_display, name="Creating Display"
        )
        display_thread.start()
        p3 = Thread(target=self._prepare_stats, name="Preparing Stats manager")
        p3.start()

        # Wait each thread to finish
        p0.join()
        p1.join()
        p3.join()

        # Loading is finished
        logger.debug(f"SETTING _is_loading {self._is_loading}")
        self._is_loading = False
        # Display thread is showing the loading screen
        display_thread.join()
        logger.info(
            "[FINISHED] Prepare to start new game. "
            "Loading Time: {} sec.".format(time.time() - start_time)
        )

    def connect(self):
        # Components are ready, we can connect them together
        self.PLOTS_MANAGER.connect()
        self.MENU_OVERLAY.connect()
        self.MODEL_MANAGER.connect()
        self.STATISTICS_MANAGER.connect()

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

        logger.debug(f"Before loop _is_loading {self._is_loading}")
        counter = 0
        while self._is_loading:
            events = pygame.event.get()
            # Look for quit events
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.USEREVENT:
                    logger.debug(event)

            self.MAIN_DISPLAY.fill("black")
            self.MAIN_DISPLAY.blit(font_surfaces[counter % 3], font_position)

            pygame.display.update()
            self.CLOCK.tick(1)
            counter += 1

        return self.MAIN_DISPLAY

    # endregion Loading

    def start_new_game(self, game: Tuple[Game, str]):
        """Start a new game."""
        pygame.init()
        self.game = game

        logger.info("Preparing the game components")
        self.prepare()

        logger.info("Connecting the game components")
        self.connect()

        logger.info("---Game Ready---")

        logger.debug(self.MODEL_MANAGER)

        # Start the simulator
        self.MODEL_THREAD.start()
        # Start the game
        self.run_game_loop()

    def run_game_loop(self):
        """Main game loop.

        TODO: The model, the plot manager and the pygame loop should run
        on separated threads.
        """
        logger.debug(f"[START] run_game_loop")

        while True:
            logger.debug(f"[START] iteration of run_game_loop")
            self.fps_counter += 1
            time_delta = self.CLOCK.tick(self.game.SETTINGS.get("FPS", 20))
            ms = self.CLOCK.get_rawtime()
            logger.debug(
                f"Game loop executed in {ms} ms, ticked {time_delta} ms."
            )
            events = pygame.event.get()
            logger.debug(f"Events: {events}")
            # Lood for quit events
            for event in events:
                self.process_event(event)

            blit = self.REGIONS_DISPLAY.listen(events)
            self.MAIN_DISPLAY.blit(self.REGIONS_DISPLAY, (0, 0))

            # Handles the actions for pygame widgets
            self.UI_MANAGER.update(time_delta / 1000.0)
            self.STATISTICS_MANAGER.UI_MANAGER.update(time_delta / 1000.0)
            self.MENU_OVERLAY.update(time_delta / 1000.0)

            self.UI_MANAGER.draw_ui(self.MAIN_DISPLAY)
            self.STATISTICS_MANAGER.UI_MANAGER.draw_ui(self.MAIN_DISPLAY)
            self.MENU_OVERLAY.draw_ui(self.MAIN_DISPLAY)

            pygame.display.update()

    # region During Game
    def process_event(self, event: Event):
        logger.info(f"Processing {event}")
        if event.type == pygame.QUIT:
            self.MODEL_MANAGER.pause()
            pygame.quit()
            sys.exit()
        elif event.type == pygame.TEXTINPUT:
            self._process_textinput_event(event)

        self.UI_MANAGER.process_events(event)
        self.MENU_OVERLAY.process_events(event)
        self.PLOTS_MANAGER.process_events(event)
        self.STATISTICS_MANAGER.process_events(event)

    def _start_new_model_thread(self):
        """Start a new thread for the model.

        Used mainly after pausing for restarting.
        """
        # Ensure the thread has ended before restarting
        if self.MODEL_THREAD.is_alive():
            logger.warn(f"{self.MODEL_THREAD} is still running.")
            return
        self.MODEL_THREAD.join()
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

    def _process_textinput_event(self, event):
        logger.debug(f"Processing TextInput.text: {event.text}.")
        match event.text:
            case " ":
                logger.debug(f"Found Space")

                self.change_model_pause_state()

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
