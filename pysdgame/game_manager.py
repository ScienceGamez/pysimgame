"""Contain a class that makes the game management."""
from __future__ import annotations
import os
import pathlib
import sys
import json
import time
import threading
from queue import Queue
from functools import cached_property
from typing import Any, Dict, Tuple
import pygame
import pygame.display
import pygame.font
import pygame_gui
from pygame_gui.ui_manager import UIManager

from .utils.pysdgame_settings import PYSDGAME_SETTINGS, SETTINGS_FILE
from .types import RegionsDict
from .menu import MenuOverlayManager, SettingsMenuManager
from .utils import recursive_dict_missing_values
from .graphs import GraphsManager
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


class GameManager:
    _game: Game
    _model_fps: float = 1
    fps_counter: int = 0
    model_manager: ModelManager = None
    _is_loading: bool = False
    _loading_screen_thread: threading.Thread
    UI_MANAGER: UIManager
    # Stores the time
    CLOCK: pygame.time.Clock

    # Dispaly for rendering everything
    MAIN_DISPLAY: pygame.Surface = None
    # Stores the policies waiting to be processed
    policy_queue: Queue[Policy]

    def _load_game_content(self):
        logger.debug(f"[START] Loading {self.game.NAME}.")
        # This will load the settings
        self.game.SETTINGS
        time.sleep(2)
        logger.debug(f"[FINISHED] Loading {self.game.NAME}.")

    @logger_enter_exit()
    def _create_display(self):

        if self.MAIN_DISPLAY is None:
            # Create a new pygame window if we don't know where to render
            self.MAIN_DISPLAY = pygame.display.set_mode(
                # First check if they are some specific game settings available
                self.game.SETTINGS.get(
                    "Resolution",
                    # Else check for PYSDGAME or set default
                    PYSDGAME_SETTINGS.get("Resolution", (1080, 720)),
                )
            )

        self._loading_screen_thread = threading.Thread(
            target=self._loading_loop
        )
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
        self.MENU_OVERLAY = MenuOverlayManager(
            self,
        )

    def _prepare_graph_display(self):
        self.GRAPHS_MANAGER = GraphsManager(
            {
                name: cmpnt.color
                for name, cmpnt in self.game.REGIONS_DICT.items()
                if name is not None
            },
            self.UI_MANAGER,
        )
        # self.GRAPHS_MANAGER.add_graph()

    @property
    def model_fps(self):
        """Get the frames per second of the model."""
        return self._model_fps

    @model_fps.setter
    def model_fps(self, new_fps: float):
        if new_fps < 0:
            raise ValueError(f"FPS must be positive not {new_fps}.")
        else:
            self._model_fps = new_fps

    def _start_model(self):
        logger.debug("[START] Starting the model")
        # Set the queue for processing of the policies
        self.policy_queue = Queue()
        # Create an instance managing the model
        self.model_manager = ModelManager(self)

        # Finds out all the policies available
        # self.policies_dict = self.model._discover_policies()

        # All possible unique policies
        # self.policies = list(set(sum(self.policies_dict.values(), [])))
        logger.debug("[FINISHED] Starting the model")
        # await asyncio.sleep(1)
        return

    def _prepare_components(self):
        # Regions have to be loaded first as they are used by the othres
        logger.info("[START] Prepare to start new game.")
        self._is_loading = True
        start_time = time.time()

        # We lauch threads here
        # At the moment it is not very efficient as all is loaded from
        # local ressource but in the future we might want to have some
        # networking processes to download some content.

        p0 = threading.Thread(
            target=self._start_model, name="Starting Model Manager"
        )
        p0.start()
        p1 = threading.Thread(
            target=self._load_game_content, name="Game Content Loading"
        )
        p1.start()
        p2 = threading.Thread(
            target=self._create_display, name="Creating Display"
        )
        p2.start()

        # Wait each thread to finish
        p0.join()
        p1.join()
        # Components are ready, we can connect them
        # self.GRAPHS_MANAGER.connect_to_model(self.model)

        # Loading is finished
        logger.debug(f"SETTING _is_loading {self._is_loading}")
        self._is_loading = False
        # Display thread is showing the loading screen
        p2.join()
        logger.info(
            "[FINISHED] Prepare to start new game. "
            "Loading Time: {} sec.".format(time.time() - start_time)
        )

    @property
    def game(self):
        """A :py:class:`Game` instance for the current game managed."""
        return self._game

    @game.setter
    def game(self, game: Tuple[Game, str]):
        if isinstance(game, str):
            # Creates the game object required
            game = Game(game)
        self._game = game
        logger.info(f"New game set: '{self._game.NAME}'.")

    def start_new_game(self, game: Tuple[Game, str]):
        """Start a new game."""
        pygame.init()
        self.game = game

        self._prepare_components()

        logger.info("---Game Ready---")

        logger.debug(self.model_manager)

        self.run_game_loop()

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
        font_position = ((x - font_surfaces[-1].get_size()[1]) / 2, y / 2)

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

    def run_game_loop(self):
        """Main game loop.

        TODO: The model, the plot manager and the pygame loop should run
        on separated threads.
        """
        logger.debug(f"[START] run_game_loop")

        while True:
            logger.debug(f"[START] iteration of run_game_loop")
            self.fps_counter += 1
            time_delta = (
                self.CLOCK.tick(self.game.SETTINGS.get("FPS", 30)) / 1000.0
            )
            events = pygame.event.get()
            logger.debug(f"Events: {events}")
            logger.debug(f"Regions Display: {self.REGIONS_DISPLAY}")
            # Lood for quit events
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                logger.debug(f"Processing {event}")
                self.UI_MANAGER.process_events(event)
                self.MENU_OVERLAY.process_events(event)

            logger.debug(f"Regions Display: {self.REGIONS_DISPLAY}")
            blit = self.REGIONS_DISPLAY.listen(events)
            logger.debug(f"MAIN_DISPLAY: {self.MAIN_DISPLAY}")
            self.MAIN_DISPLAY.blit(self.REGIONS_DISPLAY, (0, 0))

            # Handles the actions for pygame widgets
            logger.debug(f"UI_MANAGER: {self.UI_MANAGER}")
            self.UI_MANAGER.update(time_delta)
            logger.debug(f"MENU_OVERLAY: {self.MENU_OVERLAY}")
            self.MENU_OVERLAY.update(time_delta)

            if self.fps_counter % self.model_fps == 0:
                # Step of the simulation model
                self.model_manager.step()
                # Policies are applied at the step and show after

                self.GRAPHS_MANAGER.update(self.model_manager.outputs)

            logger.debug(f"[START]: drawing UI")
            self.UI_MANAGER.draw_ui(self.MAIN_DISPLAY)
            self.MENU_OVERLAY.draw_ui(self.MAIN_DISPLAY)
            logger.debug(f"[FINISHED]: drawing UI")

            pygame.display.update()

    def start_settings_menu_loop(self):
        """Open the settings menu.

        This requires no computation from the model.
        """
        menu_manager = SettingsMenuManager(self)
        while True:
            self.fps_counter += 1
            time_delta = (
                self.CLOCK.tick(self.game.SETTINGS.get("FPS", 20)) / 1000.0
            )
            events = pygame.event.get()
            # Lood for quit events
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                menu_manager.process_events(event)

            # Handles the actions for pygame widgets
            menu_manager.update(time_delta)

            self.MAIN_DISPLAY.fill("black")
            menu_manager.draw_ui(self.MAIN_DISPLAY)

            pygame.display.update()


class OldGameManager:
    """Game Manager that handles how the game works.

    Can handle any game based on a pysd simulation.

    TODO: Handle the positions of the different displays based on screen size.
    """

    BACKGROUND_COLOR = "black"
    collected_policies = {}
    GAME_DIR: str
    GRAPHS_MANAGER: GraphsManager
    UPDATE_SETTINGS: bool = True

    def __init__(self, game_name="Illuminati's Fate") -> None:

        self.GAME_DIR = os.path.join(PYSDGAME_DIR, game_name)
        if not os.path.isdir(self.GAME_DIR):
            os.mkdir(self.GAME_DIR)

        self.read_version()
        self.read_settings()

        pygame.init()
        pygame.display.set_caption(game_name)

        self.set_fps()

        self.ui_manager = pygame_gui.UIManager(
            self.PYGAME_SETTINGS["Resolution"]
        )

        self.set_game_diplays()

        self.setup_model()

    def read_version(self):
        """Should read the version and decide what to do based on it."""
        # TODO: implement something here that writes and reads the version
        self.UPDATE_SETTINGS = True

    def read_settings(self):
        """Read the user settings for that game."""
        # Check the settings exist or copy them
        settings_dir = os.path.join(self.GAME_DIR, "settings")
        if not os.path.isdir(settings_dir):
            os.mkdir(settings_dir)
        print(settings_dir)
        self.settings_file = os.path.join(settings_dir, "pygame_settings.json")
        default_file_dir = os.path.dirname(os.path.abspath(__file__))
        default_settings_file = os.path.join(
            default_file_dir, "pygame_settings.json"
        )

        if not os.path.isfile(self.settings_file) or self.UPDATE_SETTINGS:
            # Loads the default
            with open(default_settings_file) as f:
                default_settings = json.load(f)

        # Loads the user settings file

        if os.path.isfile(self.settings_file):
            with open(self.settings_file) as f:
                self.PYGAME_SETTINGS = json.load(f)
            if self.UPDATE_SETTINGS:

                # Update settings that don't exist
                recursive_dict_missing_values(
                    default_settings, self.PYGAME_SETTINGS
                )
        else:
            # Attributes the default settings
            self.PYGAME_SETTINGS = default_settings

    def save_settings(self):
        """Save the current settings in the setting file."""
        with open(self.settings_file, "w") as f:
            json.dump(self.PYGAME_SETTINGS, f, indent=2)

    def set_fps(self):
        """Set up FPS."""
        self.FramePerSec = pygame.time.Clock()
        MODEL_FPS = self.PYGAME_SETTINGS["FPS"]

        self.update_model_every = int(self.PYGAME_SETTINGS["FPS"] / MODEL_FPS)
        self.fps_counter = 0

    def set_game_diplays(self):
        # Sets the displays
        self.set_main_display()
        self.set_regions_display()
        self.set_graph_display()
        self.set_menu_displays()

    def set_main_display(self):
        """Set up the 'big window' of the game."""
        self.MAIN_DISPLAY = pygame.display.set_mode(
            self.PYGAME_SETTINGS["Resolution"]
        )

    def set_regions_display(self):
        self.REGIONS_DISPLAY = RegionsSurface(
            self, on_region_selected=self.on_region_selected
        )
        self.MAIN_DISPLAY.blit(self.REGIONS_DISPLAY, (0, 0))

    def set_menu_displays(self):
        """Set up the menu displayer of the game.

        Menu buttons are set at the top right.
        """
        self.MENU_OVERLAY = MenuOverlayManager(
            self,
        )

    def on_region_selected(self):
        logger.info(
            "region '{}' selected".format(
                self.REGIONS_DISPLAY.selected_region.name
            )
        )

    def set_graph_display(self):
        self.GRAPHS_MANAGER = GraphsManager(
            {
                name: cmpnt.color
                for name, cmpnt in self.REGIONS_DISPLAY.region_components.items()
                if name is not None
            },
            self.ui_manager,
        )
        self.GRAPHS_MANAGER.add_graph()

    def setup_model(self):
        """Set up the model and the different policies applicable."""

        self.model = ModelManager(
            self,
        )

        # Finds out all the policies available
        self.policies_dict = self.model._discover_policies()

        # All possible unique policies
        self.policies = list(set(sum(self.policies_dict.values(), [])))

        # Connects to the graphs manager
        self.GRAPHS_MANAGER.connect_to_model(self.model)

    def add_policy(self, region, policy):
        if region not in self.collected_policies:
            self.collected_policies[region] = []
        self.collected_policies[region].append(policy)
