"""Contain a class that makes the game management."""
from __future__ import annotations
import os
import sys
import json
import pygame
from pygame import display
import pygame_gui
import pygame_widgets

from .menu import MenuOverlayManager, SettingsMenuManager
from .utils import recursive_dict_missing_values
from .graphs import GraphsManager
from .regions_display import RegionsSurface
from .model import ModelManager

from .utils.directories import PYSDGAME_DIR


class GameManager:
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
        self.MAIN_DISPLAY = display.set_mode(
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
        print(self.REGIONS_DISPLAY.selected_region.name)

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

            display.update()

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

            display.update()
