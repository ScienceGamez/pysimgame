"""Contain a class that makes the game management."""
from __future__ import annotations
import os
import pathlib
import sys
import json
import time
import asyncio
import threading
from functools import cached_property
from typing import Any, Dict, Tuple
import pygame
import pygame.display
import pygame_gui


from .utils.pysdgame_settings import PYSDGAME_SETTINGS
from .types import DirPath, RegionsDict
from .menu import MenuOverlayManager, SettingsMenuManager
from .utils import recursive_dict_missing_values
from .graphs import GraphsManager
from .regions_display import RegionComponent, RegionsSurface
from .model import ModelManager
from .utils.logging import logger

from .utils.directories import PYSDGAME_DIR, REGIONS_FILE_NAME


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
        self.PYSD_MODEL_FILE = pathlib.Path(self.GAME_DIR, REGIONS_FILE_NAME)

    @cached_property
    def REGIONS_DICT(self) -> RegionsDict:
        """Load the dictionary of the regions for that game."""
        with open(self.REGIONS_FILE, "r") as f:
            dic = json.load(f)
        logger.info("Region file loaded.")
        logger.debug(f"Region file content: {dic}.")

        return {
            region_dict["name"]: RegionComponent.from_dict(region_dict)
            for region_dict in dic.values()
        }


class GameManager:
    _game: Game
    GAME_SETTINGS: Dict[str, Any]
    _model_fps: float = 1
    model_manager: ModelManager = None

    def _load_game_content(self):
        logger.debug(f"[START] Loading {self.game.NAME}.")
        time.sleep(5)
        logger.debug(f"[FINISHED] Loading {self.game.NAME}.")

    def _create_display(self):
        logger.debug("[START] Setting the display.")
        time.sleep(10)
        logger.debug("[FINISHED] Setting the display.")

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
        processes = []
        for f in self._load_game_content, self._create_display:
            p = threading.Thread(target=f)
            p.start()
            processes.append(p)
        for p in processes:
            p.join()
        # Components are ready, we can connect them
        # self.GRAPHS_MANAGER.connect_to_model(self.model)

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
        """Start a new game"""
        self.game = game
        logger.debug("[START] Prepare to start new game.")
        start = time.time()
        threading.Thread(target=self._start_model).start()
        self._prepare_components()
        logger.debug("[FINISHED] Prepare to start new game.")
        print(time.time() - start)
        logger.info("---Game Ready---")


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

    def start_game_loop(self):

        while True:
            self.fps_counter += 1
            time_delta = (
                self.FramePerSec.tick(self.PYGAME_SETTINGS["FPS"]) / 1000.0
            )
            events = pygame.event.get()
            # Lood for quit events
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                self.ui_manager.process_events(event)
                self.MENU_OVERLAY.process_events(event)

            blit = self.REGIONS_DISPLAY.listen(events)
            self.MAIN_DISPLAY.blit(self.REGIONS_DISPLAY, (0, 0))

            # Handles the actions for pygame widgets
            self.ui_manager.update(time_delta)
            self.MENU_OVERLAY.update(time_delta)

            if self.fps_counter % self.update_model_every == 0:
                # Step of the simulation model
                self.model.step()
                # Policies are applied at the step and show after
                self.model.apply_policies(self.collected_policies)
                self.collected_policies = {}
                self.GRAPHS_MANAGER.update(self.model.outputs)

            self.ui_manager.draw_ui(self.MAIN_DISPLAY)
            self.MENU_OVERLAY.draw_ui(self.MAIN_DISPLAY)

            pygame.display.update()

    def start_settings_menu_loop(self):
        """Open the settings menu.

        This requires no computation from the model.
        """
        menu_manager = SettingsMenuManager(self)
        while True:
            self.fps_counter += 1
            time_delta = (  # Smaller tickrate is okay for the setting menu
                self.FramePerSec.tick(20) / 1000.0
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
