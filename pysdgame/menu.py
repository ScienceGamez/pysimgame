"""A class that handles the menu of the game."""
from __future__ import annotations


from typing import TYPE_CHECKING
import pygame
from pygame_gui.core.ui_element import ObjectID

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

        screen_resolution = game_manager.MAIN_DISPLAY.get_size()
        print(game_manager.PYGAME_SETTINGS["Themes"]["Menu"])
        super().__init__(
            screen_resolution,
            theme_path=game_manager.PYGAME_SETTINGS["Themes"]["Menu"],
        )
        buttons_size = relative_height * screen_resolution[1]

        def create_rect(i):
            """Create a pygame.Rect for the i-eth button."""
            return pygame.Rect(
                screen_resolution[0] - (i + 1) * buttons_size,
                0,
                buttons_size,
                buttons_size,
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
