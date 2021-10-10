"""Contain a class that makes the game management."""
from __future__ import annotations
import os
import sys
import json
import pygame
from pygame import display
import pygame_widgets

from .graphs import GraphsSurface
from .regions_display import RegionsSurface
from .model import ModelManager

from .utils.directories import PYSDGAME_DIR


class GameManager:
    """Game Manager that handles how the game works.

    Can handle any game based on a pysd simulation.

    TODO: Handle the positions of the different displays based on screen size.
    """

    BACKGROUND_COLOR = 'black'
    collected_policies = {}
    GAME_DIR: str
    UPDATE_SETTINGS: bool



    def __init__(
        self, game_name="Illuminati's Fate"
    ) -> None:

        self.GAME_DIR = os.path.join(PYSDGAME_DIR, game_name)
        if not os.path.isdir(self.GAME_DIR):
            os.mkdir(self.GAME_DIR)

        self.read_version()
        self.read_settings()

        pygame.display.set_caption(game_name)
        self.set_fps()
        self.set_game_diplays()

        self.setup_model()

        # Tracks all widgets
        self.widgets = []

    def read_version(self):
        """Should read the version and decide what to do based on it."""
        # TODO: implement something here that writes and reads the version
        self.UPDATE_SETTINGS = True

    def read_settings(self):
        """Read the user settings for that game."""
        # Check the settings exist or copy them
        settings_dir = os.path.join(self.GAME_DIR, 'settings')
        if not os.path.isdir(settings_dir):
            os.mkdir(settings_dir)

        settings_file = os.path.join(settings_dir, 'pygame_settings.json')
        default_file_dir = os.path.dirname(os.path.abspath(__file__))
        default_settings_file = os.path.join(
            default_file_dir, 'pygame_settings.json'
        )

        if not os.path.isfile(settings_file) or self.UPDATE_SETTINGS:
            # Loads the default
            with open(default_settings_file) as f:
                default_settings = json.load(f)

        # Loads the user settings file
        if os.path.isfile(settings_file):
            with open(settings_file) as f:
                self.PYGAME_SETTINGS = json.load(f)
            if self.UPDATE_SETTINGS:
                # Update settings that don't exist
                for key, items in default_settings:
                    if key not in self.PYGAME_SETTINGS:
                        self.PYGAME_SETTINGS[key] = items
        else:
            # Attributes the default settings
            self.PYGAME_SETTINGS = default_settings


    def set_fps(self):
        """Set up FPS."""
        self.FramePerSec = pygame.time.Clock()
        MODEL_FPS = 20

        self.update_model_every = int(self.PYGAME_SETTINGS["FPS"]/MODEL_FPS)

    def set_game_diplays(self):
        # Sets the displays
        self.set_main_display()
        self.set_regions_display()
        self.set_graph_display()

    def set_main_display(self):
        """Set up the 'big window' of the game."""
        self.MAIN_DISPLAY = display.set_mode(
            self.PYGAME_SETTINGS["Resolution"]
        )

    def set_regions_display(self):
        self.EARTH_DISPLAY = RegionsSurface(
            self,
            on_region_selected=self.on_region_selected
        )
        self.MAIN_DISPLAY.blit(self.EARTH_DISPLAY, (0, 0))

    def on_region_selected(self):
        print(self.EARTH_DISPLAY.selected_region.name)

    def set_graph_display(self):
        self.GRAPHS_DISPLAY = GraphsSurface(
            (1080, 720),
            region_colors_dict={
                name: cmpnt.color
                for name, cmpnt in self.EARTH_DISPLAY.region_components.items()
                if name is not None
            },
        )
        self.MAIN_DISPLAY.blit(self.GRAPHS_DISPLAY, (1080, 0))

    def add_widget(self, widget):
        self.widgets.append(widget)


    def setup_model(self):
        """Set up the model and the different policies applicable."""
        # First get the elements to be shown. TODO: improve this
        self.capture_elements = [
            'gdp_per_capita',
            'population',
            'desired_food_ratio'
        ]

        regions_names = list(self.EARTH_DISPLAY.region_components.keys())
        regions_names.remove(None)  # Fake value
        self.model = IlluminatisModel(
            regions_names,
            self.capture_elements
        )

        # Finds out all the policies available
        self.policies_dict = self.model._discover_policies()

        # All possible unique policies
        self.policies = list(set(sum(self.policies_dict.values(), [])))

    def add_policy(self, region, policy):
        if region not in self.collected_policies:
            self.collected_policies[region] = []
        self.collected_policies[region].append(policy)

    def start_game_loop(self):
        # Game loop begins
        fps_counter = 0

        while True:
            fps_counter += 1
            events = pygame.event.get()
            # Lood for quit events
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            blit = self.EARTH_DISPLAY.listen(events)
            if blit:
                self.MAIN_DISPLAY.blit(self.EARTH_DISPLAY, (0,0))

            # Handles the actions for pygame widgets
            pygame_widgets.update(events)


            if fps_counter % self.update_model_every == 0:
                # Step of the simulation model
                self.model.step()
                # Policies are applied at the step and show after
                self.model.apply_policies(self.collected_policies)
                self.collected_policies = {}
                self.GRAPHS_DISPLAY.plot(self.model.outputs)
                self.MAIN_DISPLAY.blit(
                    self.GRAPHS_DISPLAY,
                    self.EARTH_DISPLAY.get_rect().topright
                )

            display.update()
            self.FramePerSec.tick(self.PYGAME_SETTINGS["FPS"])