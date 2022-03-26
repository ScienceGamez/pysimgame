"""A class that handles the menu of the game.

The main buttons are handled by MenuOverlayManager.
The menu which is openable from that MenuOverlayMangaer is handled by
SettingsMenuManager.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pygame
from pygame.event import Event

from pysimgame import PYSDGAME_SETTINGS
from pysimgame.statistics import StatisticsDisplayManager
from pysimgame.utils import GameComponentManager
from pysimgame.utils.directories import THEMES_DIR
from pysimgame.utils.dynamic_menu import UISettingsMenu

if TYPE_CHECKING:
    from pysimgame.game_manager import GameManager
    from pysimgame.plotting.manager import PlotsManager

import pygame_gui
from pygame_gui import UIManager
from pygame_gui.elements import UIButton


class MenuOverlayManager(GameComponentManager):
    """Class that handles the menu of the game."""

    PLOTS_MANAGER: PlotsManager
    STATISTICS_MANAGER: StatisticsDisplayManager
    UI_MANAGER: UIManager

    def __init__(self, GAME_MANAGER: GameManager) -> None:
        """Initialize the Menu overlay of the game.

        Args:
            GAME_MANAGER: The game manager.
        """
        GameComponentManager.__init__(self, GAME_MANAGER)

    def prepare(self, relative_height: float = 0.07):
        # TODO: see how we want to make the relative height a setting

        screen_resolution = self.GAME_MANAGER.MAIN_DISPLAY.get_size()
        game_menu_theme_path = Path(
            THEMES_DIR, PYSDGAME_SETTINGS["Themes"]["Game Menu"]
        )
        self.logger.debug(f"Theme for Menu: {game_menu_theme_path}")
        self.UI_MANAGER = UIManager(
            screen_resolution,
            theme_path=game_menu_theme_path,
        )
        self.buttons_size = relative_height * screen_resolution[1]

        def create_rect(i):
            """Create a pygame.Rect for the i-eth button."""
            return pygame.Rect(
                screen_resolution[0] - (i + 1) * self.buttons_size,
                0,
                self.buttons_size,
                self.buttons_size,
            )

        self.overlay_buttons = [
            UIButton(
                create_rect(0),
                text="",
                manager=self.UI_MANAGER,
                object_id="#open_menu_button",
            ),
            UIButton(
                create_rect(1),
                text="",
                manager=self.UI_MANAGER,
                object_id="#help_button",
            ),
            UIButton(
                create_rect(2),
                text="",
                manager=self.UI_MANAGER,
                object_id="#plots_button",
            ),
            UIButton(
                create_rect(3),
                text="",
                manager=self.UI_MANAGER,
                object_id="#stats_button",
            ),
            UIButton(
                create_rect(4),
                text="",
                manager=self.UI_MANAGER,
                object_id="#regions_button",
            ),
        ]

    def connect(self):
        self.PLOTS_MANAGER = self.GAME_MANAGER.PLOTS_MANAGER
        self.STATISTICS_MANAGER = self.GAME_MANAGER.STATISTICS_MANAGER

    def process_events(self, event: Event):
        handled = self.UI_MANAGER.process_events(event)

        if event.type != pygame.USEREVENT:
            # gui events are USERVENT
            return

        if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_object_id == "#help_button":
                self.logger.error("no help lol")
                handled = True
            elif event.ui_object_id == "#open_menu_button":
                # Will open the menu
                self.GAME_MANAGER.MODEL_MANAGER.pause()
                self.GAME_MANAGER.start_settings_menu_loop()

                # When the menu is closed, this code continues here
                handled = True

            elif event.ui_object_id == "#stats_button":
                # Will show or hide the stats
                if self.STATISTICS_MANAGER._hidden:
                    self.STATISTICS_MANAGER.show()
                else:
                    self.STATISTICS_MANAGER.hide()

        return handled


class SettingsMenuManager(pygame_gui.UIManager):
    """Manager for the setting menu."""

    GAME_MANAGER: GameManager

    def __init__(self, GAME_MANAGER: GameManager):
        self.GAME_MANAGER = GAME_MANAGER
        display_size = GAME_MANAGER.MAIN_DISPLAY.get_size()
        super().__init__(
            display_size,
            theme_path=PYSDGAME_SETTINGS["Themes"]["Settings"],
        )

        def start_game_loop_decorator(func):
            def decorated_func(*args, **kwargs):
                ret = func(*args, **kwargs)
                self.GAME_MANAGER.run_game_loop()

            return decorated_func

        self.menu = UISettingsMenu(
            GAME_MANAGER.MAIN_DISPLAY.get_rect(),
            self,
            PYSDGAME_SETTINGS,
        )

        # When the menu is killed, go back to game
        self.menu.kill = start_game_loop_decorator(self.menu.kill)
