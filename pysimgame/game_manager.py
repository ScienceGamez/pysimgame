"""Contain a class that makes the game management."""
from __future__ import annotations

import concurrent.futures
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
from pysimgame.links.manager import LinksManager
from pysimgame.speed import SpeedManager
from pysimgame.statistics import StatisticsDisplayManager
from pysimgame.utils import logging

from .menu import MenuOverlayManager, SettingsMenuManager
from .model import ModelManager, Policy
from .plots import PlotsManager
from .regions_display import (
    RegionComponent,
    RegionsManager,
    SingleRegionComponent,
)
from .utils import GameComponentManager, recursive_dict_missing_values
from .utils.directories import (
    GAME_SETTINGS_FILENAME,
    INITIAL_CONDITIONS_FILENAME,
    MODEL_FILENAME,
    PYSDGAME_DIR,
    REGIONS_FILE_NAME,
)
from .utils.logging import logger, logger_enter_exit
from .utils.pysimgame_settings import PYSDGAME_SETTINGS, SETTINGS_FILE

if TYPE_CHECKING:
    from .types import ModelType, RegionsDict


BACKGROUND_COLOR = "black"

_GAME_MANAGER: GameManager = None


def get_game_manager() -> GameManager:
    if _GAME_MANAGER is not None:
        return _GAME_MANAGER
    else:
        game_manager = GameManager()
        return get_game_manager()


def get_model_manager() -> ModelManager:
    return get_game_manager().MODEL_MANAGER


class Game:
    """Helper class representing a game type from pysd.

    Holds meta information on a game.
    Games all have a model they are based on and a set of settings to
    define how they should be played.
    """

    NAME: str
    GAME_DIR: pathlib.Path
    REGIONS_FILE: pathlib.Path
    INITIAL_CONDITIONS_FILE: pathlib.Path
    PYSD_MODEL_FILE: pathlib.Path
    SETTINGS: Dict[str, Any]

    REGIONS_DICT: RegionsDict

    def __new__(cls, name: str | Game, *args, **kwargs):
        if isinstance(name, cls):
            # Return the game if a game object was given
            return name
        else:
            return object.__new__(cls)

    def __init__(self, name: str | Game, create: bool = False) -> None:
        self.NAME = name
        self.GAME_DIR = pathlib.Path(PYSDGAME_DIR, name)
        match self.GAME_DIR.exists(), create:
            case False, True:  # Game creation
                self.GAME_DIR.mkdir()
            case False, False:  # Reading a non existing game
                raise RuntimeError(f"Game '{name}' cannot be found.")
        self.REGIONS_FILE = pathlib.Path(self.GAME_DIR, REGIONS_FILE_NAME)
        self.PYSD_MODEL_FILE = pathlib.Path(self.GAME_DIR, MODEL_FILENAME)
        self.INITIAL_CONDITIONS_FILE = pathlib.Path(
            self.GAME_DIR, INITIAL_CONDITIONS_FILENAME
        )
        self._SETTINGS_FILE = pathlib.Path(
            self.GAME_DIR, GAME_SETTINGS_FILENAME
        )

    @cached_property
    def SINGLE_REGION(self) -> bool:
        """Whether the game has only one region."""
        return len(self.REGIONS_DICT) <= 1

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

    def load_model(self) -> ModelType:
        """Return a model object for doc purposes.

        ..note:: currently works only with pysd models.
        """
        import pysd

        model = pysd.load(self.PYSD_MODEL_FILE)
        return model.components


class GameManager(GameComponentManager):
    """Main component of the game.

    Organizes the other components managers from the game.
    It is required for the game manager to run on the main thread.
    """

    ## GAME manager MUST be run on a main thread !
    _game: Game
    _model_fps: float = 1
    fps_counter: int = 0
    _is_loading: bool = False
    _loading_screen_thread: Thread

    # Components managers
    MANAGERS: Dict[str, GameComponentManager]
    _manager_classes = List[Type[GameComponentManager]]
    MODEL_MANAGER: ModelManager
    PLOTS_MANAGER: PlotsManager
    STATISTICS_MANAGER: StatisticsDisplayManager
    ACTIONS_MANAGER: ActionsManager
    REGIONS_MANAGER: RegionsManager
    MENU_OVERLAY: MenuOverlayManager
    # Stores the time
    CLOCK: pygame.time.Clock

    # Dispaly for rendering everything
    MAIN_DISPLAY: pygame.Surface = None
    # Stores the policies waiting to be processed
    policy_queue: Queue[Policy]

    def __init__(self) -> None:
        """Override the main :py:class:`GameManager` is the main organizer."""
        global _GAME_MANAGER
        if _GAME_MANAGER is None:
            _GAME_MANAGER = self
        # TODO, see if there is a better way to set that
        # Think about modding(different games), threading,  and UI positioning
        self._manager_classes = [
            RegionsManager,
            MenuOverlayManager,
            PlotsManager,
            ModelManager,
            ActionsGUIManager,
            StatisticsDisplayManager,
            ActionsManager,
            SpeedManager,
            LinksManager,
        ]
        self.MANAGERS = {}

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
        # TODO: add the theme path
        self.UI_MANAGER = UIManager(self.MAIN_DISPLAY.get_size())
        # Set the queue for processing of the policies
        self.policy_queue = Queue()

        # Launch a thread for the loading display
        loading_thread = Thread(target=self._loading_loop, name="Loading")
        loading_thread.start()

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
            thread_name_prefix="managerPrepare"
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

        logger.info(f"MANAGERS : {self.MANAGERS}")
        # Assign some specific managers as variable
        # TODO: make this more moddable by using different classes ?
        # Ex. a find ___ manager method
        self.MODEL_MANAGER = self.MANAGERS[ModelManager]
        self.PLOTS_MANAGER = self.MANAGERS[PlotsManager]
        self.STATISTICS_MANAGER = self.MANAGERS[StatisticsDisplayManager]
        self.ACTIONS_MANAGER = self.MANAGERS[ActionsManager]
        self.REGIONS_MANAGER = self.MANAGERS[RegionsManager]
        self.MENU_OVERLAY = self.MANAGERS[MenuOverlayManager]

        # Model will run on a separated thread
        self.MODEL_THREAD = Thread(
            target=self.MODEL_MANAGER.run, name="ModelThread"
        )

        # Loading is finished (used in the loading screen loop)
        logger.debug(f" _is_loading {self._is_loading}")
        self._is_loading = False
        # Display thread is showing the loading screen
        loading_thread.join()
        logger.info(
            "[FINISHED] Prepare to start new game. "
            "Loading Time: {} sec.".format(time.time() - start_time)
        )

    def connect(self):
        # Components are ready, we can connect them together
        for manager in self.MANAGERS.values():
            manager.connect()

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
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                ):
                    print("Quit")
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.USEREVENT:
                    logger.debug(f"User Event : {event}")

            self.MAIN_DISPLAY.fill(BACKGROUND_COLOR)
            self.MAIN_DISPLAY.blit(font_surfaces[counter % 3], font_position)

            pygame.display.update()
            self.CLOCK.tick(1)
            counter += 1

        return self.MAIN_DISPLAY

    # endregion Loading
    def load(self, save_file: pathlib.Path):
        """Load a game from the save.

        TODO: Implement
        Idea: make every manager save in a file what they need and then
        compress into a file.
        """
        save_dir = save_file.parent
        for manager in self.MANAGERS.values():
            manager.load(save_dir)

    def start_new_game(
        self, game: Tuple[Game, str], from_save: pathlib.Path = None
    ):
        """Start a new game."""
        pygame.init()
        self.game = game

        logger.info("Preparing the game components")
        self.prepare()

        if from_save:
            logger.info(f"Loading from save {from_save}")
            self.load(from_save)
            logger.info(f"Save loaded {from_save}")

        logger.info("Connecting the game components")
        self.connect()

        logger.info("---Game Ready---")

        logger.debug(self.MODEL_MANAGER)

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

            self.MAIN_DISPLAY.fill(BACKGROUND_COLOR)

            self.REGIONS_MANAGER.update()

            self.UI_MANAGER.update(time_delta / 1000.0)
            for manager in self.MANAGERS.values():
                if hasattr(manager, "UI_MANAGER"):
                    # Handles the actions for pygame_gui UIManagers
                    manager.UI_MANAGER.update(time_delta / 1000.0)
                manager.draw()

            self.UI_MANAGER.draw_ui(self.MAIN_DISPLAY)
            self.STATISTICS_MANAGER.UI_MANAGER.draw_ui(self.MAIN_DISPLAY)
            self.MENU_OVERLAY.UI_MANAGER.draw_ui(self.MAIN_DISPLAY)

            pygame.display.update()

    def process_event(self, event: Event):
        logger.debug(f"Processing {event}")
        self.UI_MANAGER.process_events(event)
        match event:
            case EventType(type=pygame.QUIT) | EventType(
                type=pygame.KEYDOWN, key=pygame.K_ESCAPE
            ):
                self.MODEL_MANAGER.pause()
                pygame.quit()
                sys.exit()
            case EventType(type=pygame.TEXTINPUT):
                self._process_textinput_event(event)
            case EventType(type=pysimgame.events.TogglePaused):
                self.change_model_pause_state()

        for manager in self.MANAGERS.values():
            manager.process_events(event)

    def _start_new_model_thread(self):
        """Start a new thread for the model.

        Used mainly after pausing for restarting.
        """
        # Ensure the thread has ended before restarting
        if self.MODEL_THREAD.is_alive():
            logger.warn(f"{self.MODEL_THREAD} is still running.")
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
