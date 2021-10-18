"""A class that handles the menu of the game.

The main buttons are handled by MenuOverlayManager.
The menu which is openable from that MenuOverlayMangaer is handled by
SettingsMenuManager.
"""
from __future__ import annotations


from typing import TYPE_CHECKING
import pygame
from pygame.event import Event
from pygame_gui.core.ui_element import ObjectID
from pygame_gui.elements.ui_panel import UIPanel
from pygame_gui.elements.ui_selection_list import UISelectionList

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

    def process_events(self, event: Event):
        handled = super().process_events(event)

        if event.type != pygame.USEREVENT:
            # gui events are USERVENT
            return

        if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_object_id == "#help_button":
                print("no help lol")
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
        display_size = game_manager.MAIN_DISPLAY.get_size()
        super().__init__(
            display_size,
            theme_path=game_manager.PYGAME_SETTINGS["Themes"]["Settings"],
        )

        self.scrolling_container = pygame_gui.elements.UIScrollingContainer(
            pygame.Rect(0, 0, display_size[0] - 30, display_size[1] - 30),
            self,
        )
        self.scrolling_container.set_scrollable_area_dimensions((1000, 4000))
        self.test_box = pygame_gui.elements.UITextBox(
            "Hello",
            pygame.Rect(50, 50, 200, 100),
            self,
            container=self.scrolling_container.get_container(),
            parent_element=self.scrolling_container,
        )
        self.test_button = pygame_gui.elements.UIButton(
            pygame.Rect(250, 150, 100, 100),
            "Test",
            self,
            self.scrolling_container.get_container(),
        )
        self.test_button2 = pygame_gui.elements.UIButton(
            pygame.Rect(250, 3150, 100, 100),
            "Test",
            self,
            self.scrolling_container,
        )

        # self.scroll_bar = pygame_gui.elements.UIVerticalScrollBar(
        #    pygame.Rect(display_size[0] - 20, 0, 20, display_size[1]),
        #    0.2,
        #    self,
        # )
