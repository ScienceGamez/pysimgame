"""A class that handles the menu of the game.

The main buttons are handled by MenuOverlayManager.
The menu which is openable from that MenuOverlayMangaer is handled by
SettingsMenuManager.
"""
from __future__ import annotations


from typing import TYPE_CHECKING
import pygame
from pygame.event import Event

from pysdgame import PYSDGAME_SETTINGS
from pysdgame.utils.logging import logger

from pysdgame.utils.dynamic_menu import UISettingsMenu

if TYPE_CHECKING:
    from pysdgame.game_manager import GameManager

import pygame_gui
from pygame_gui.elements import UIButton


class MenuOverlayManager(pygame_gui.UIManager):
    """Class that handles the menu of the game."""

    GAME_MANAGER: GameManager

    def __init__(
        self, game_manager: GameManager, relative_height: float = 0.07
    ) -> None:
        """Initialize the Menu overlay of the game.

        Args:
            game_manager: The game manager.
        """
        self.GAME_MANAGER = game_manager

        screen_resolution = game_manager.rendrered_surface.get_size()
        logger.debug(
            "Theme for Menu: {}".format(PYSDGAME_SETTINGS["Themes"]["Menu"])
        )
        super().__init__(
            screen_resolution,
            theme_path=PYSDGAME_SETTINGS["Themes"]["Menu"],
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
                manager=self,
                object_id="#open_menu_button",
            ),
            UIButton(
                create_rect(1),
                text="",
                manager=self,
                object_id="#help_button",
            ),
            UIButton(
                create_rect(2),
                text="",
                manager=self,
                object_id="#graphs_button",
            ),
            UIButton(
                create_rect(3),
                text="",
                manager=self,
                object_id="#stats_button",
            ),
            UIButton(
                create_rect(4),
                text="",
                manager=self,
                object_id="#regions_button",
            ),
        ]

    def process_events(self, event: Event):
        handled = super().process_events(event)

        if event.type != pygame.USEREVENT:
            # gui events are USERVENT
            return

        if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_object_id == "#help_button":
                logger.error("no help lol")
                handled = True
            elif event.ui_object_id == "#open_menu_button":
                # Will open the menu
                self.GAME_MANAGER.start_settings_menu_loop()
                # When the menu is closed, this code continues here
                handled = True

        return handled


class SettingsMenuManager(pygame_gui.UIManager):
    """Manager for the setting menu."""

    GAME_MANAGER: GameManager

    def __init__(self, game_manager: GameManager):
        self.GAME_MANAGER = game_manager
        display_size = game_manager.rendrered_surface.get_size()
        super().__init__(
            display_size,
            theme_path=PYSDGAME_SETTINGS["Themes"]["Settings"],
        )

        def start_game_loop_decorator(func):
            def decorated_func(*args, **kwargs):
                ret = func(*args, **kwargs)
                self.GAME_MANAGER.start_game_loop()

            return decorated_func

        self.menu = UISettingsMenu(
            game_manager.rendrered_surface.get_rect(),
            self,
            PYSDGAME_SETTINGS,
        )

        # When the menu is killed, go back to game
        self.menu.kill = start_game_loop_decorator(self.menu.kill)
