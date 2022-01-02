from typing import Dict, List, Tuple

import pygame
import pygame_gui
from pygame.constants import TEXTINPUT
from pygame.event import EventType
from pygame_gui.core import UIContainer
from pygame_gui.elements import UIButton, UITextBox
from pygame_gui.elements.ui_label import UILabel
from pygame_gui.ui_manager import UIManager

import pysimgame
from pysimgame.utils import GameComponentManager, pysimgame_settings


class SpeedManager(GameComponentManager):
    """Manager of the model speed."""

    speed: float
    available_speeds: List[float]

    container: UIContainer
    play_button: UIButton
    faster_button: UIButton
    slower_button: UIButton
    speed_label: UILabel

    settings: Dict

    def _resize_ui(self):
        """Recreate the ui to the size"""

        x, y = self.GAME_MANAGER.MAIN_DISPLAY.get_size()

        rect: pygame.Rect = self.settings["container_rect"]
        rect.x = (x - rect.width) / 2
        rect.y = y - rect.height

        self.speed = 1

        self.container = UIContainer(
            relative_rect=self.settings["container_rect"],
            manager=self.ui_manager,
        )

        self.play_button = UIButton(
            relative_rect=self.settings["play_rect"],
            text=">",
            manager=self.ui_manager,
            container=self.container,
        )
        self.faster_button = UIButton(
            relative_rect=self.settings["faster_rect"],
            text="+",
            manager=self.ui_manager,
            container=self.container,
        )
        self.slower_button = UIButton(
            relative_rect=self.settings["slower_rect"],
            text="-",
            manager=self.ui_manager,
            container=self.container,
        )

        self.speed_label = UILabel(
            relative_rect=self.settings["text_rect"],
            text=f"{self.speed} X",
            manager=self.ui_manager,
            container=self.container,
        )

    def prepare(self):
        self.settings = {
            "available_speeds": [1 / 4, 1 / 2, 1, 2, 4, 10],
            "container_rect": pygame.Rect(-1, 500, 200, 50),
            "play_rect": pygame.Rect(0, 0, 50, 50),
            "faster_rect": pygame.Rect(175, 0, 25, 25),
            "slower_rect": pygame.Rect(175, 25, 25, 25),
            "text_rect": pygame.Rect(50, 0, 125, 50),
        }
        # Uses the game manager ui
        self.ui_manager = self.GAME_MANAGER.UI_MANAGER
        self.available_speeds = sorted(self.settings["available_speeds"])
        self._resize_ui()

    def connect(self):
        self.MODEL_MANAGER = self.GAME_MANAGER.MODEL_MANAGER
        self._base_fps = self.MODEL_MANAGER.fps

    def increase_speed(self):
        """Increase the speed.

        1 step in the available speeds.
        """
        # Gets the current speed
        ind = self.available_speeds.index(self.speed)
        if ind < len(self.available_speeds) - 1:
            # Calculate the new speed index (assume sorted)
            self.speed = self.available_speeds[int(ind + 1)]
            self.post_changed_speed()

    def decrease_speed(self):
        """Decrease the speed.

        1 step in the available speeds.
        """
        # Gets the current speed
        ind = self.available_speeds.index(self.speed)
        if ind > 0:
            # Calculate the new speed index (assume sorted)
            self.speed = self.available_speeds[int(ind - 1)]
            self.post_changed_speed()

    def post_changed_speed(self):
        # post event
        event = pygame.event.Event(
            pysimgame.events.SpeedChanged,
            {"fps": self._base_fps * self.speed},
        )
        pygame.event.post(event)

    def process_events(self, event: pygame.event.Event):
        """Listen the events for this manager."""
        match event:

            case EventType(
                type=pygame_gui.UI_BUTTON_PRESSED,
                ui_element=self.faster_button,
            ) | EventType(type=pygame.TEXTINPUT, text="+"):
                self.increase_speed()

            case EventType(
                type=pygame_gui.UI_BUTTON_PRESSED,
                ui_element=self.slower_button,
            ) | EventType(type=pygame.TEXTINPUT, text="-"):
                self.decrease_speed()

            case EventType(type=pysimgame.events.SpeedChanged):
                self.speed_label.set_text(f"{self.speed} X")
            case EventType(
                type=pygame_gui.UI_BUTTON_PRESSED,
                ui_element=self.play_button,
            ):
                # Change the pause state
                event = pygame.event.Event(pysimgame.events.TogglePaused, {})
                pygame.event.post(event)
            case EventType(type=pysimgame.events.Paused):
                self.play_button.set_text("||")
            case EventType(type=pysimgame.events.UnPaused):
                self.play_button.set_text(">")
