"""GUI for the actions."""

from typing import TYPE_CHECKING

import pygame
from pygame_gui.elements import UIButton, UIWindow
from pygame_gui.ui_manager import UIManager
from pysdgame.actions.actions import ActionsDict, BaseAction
from pysdgame.utils import GameComponentManager
from pysdgame.utils.directories import THEME_FILENAME, THEMES_DIR
from pysdgame.utils.dynamic_menu import UIColumnContainer

if TYPE_CHECKING:
    from .actions import ActionsManager


class ActionsGUIManager(GameComponentManager):
    UI_MANAGER: UIManager
    ACTIONS_MANAGER: ActionsManager

    def prepare(self):
        # Create a ui manager for this component
        display_size = self.GAME_MANAGER.MAIN_DISPLAY.get_size()
        self.UI_MANAGER = UIManager(
            display_size,
            self.GAME.SETTINGS["Theme"].get("actions", "default"),
        )
        window = UIWindow(
            pygame.Rect(100, 100, 500, 500),
            manager=UIManager,
            window_display_title="Actions",
            resizable=True,
        )
        self.CONTAINER = UIColumnContainer(
            window.window_element_container.get_relative_rect(),
            manager=UIManager,
            container=window.window_element_container,
            parent_element=window,
        )

    def connect(self):
        """Connect to the actions."""
        self.ACTIONS_MANAGER = self.GAME_MANAGER.ACTIONS_MANAGER
        self._create_actions_menu(self.ACTIONS_MANAGER.actions)

    def _create_actions_menu(self, actions_dict: ActionsDict):
        """Create the buttons with the actions for the actions dict."""
        h = 40
        w = self.CONTAINER.get_relative_rect().width
        for name, action in actions_dict.items():
            # Recursively add buttons for the actions

            if isinstance(action, dict):
                # Create a button that triggers the action
                button = UIButton(
                    relative_rect=pygame.Rect(0, 0, w, h),
                    text=name,
                    manager=self.UI_MANAGER,
                    container=self.CONTAINER,
                    object_id="#actions_type_button",
                )
            elif isinstance(action, BaseAction):
                # Create a button to trigger
                button = UIButton(
                    relative_rect=pygame.Rect(0, 0, w, h),
                    text=name,
                    manager=self.UI_MANAGER,
                    container=self.CONTAINER,
                    object_id="#action_button",
                )
            else:
                raise TypeError(
                    f"Invalid type in ActionsDict : {type(action)}."
                    "Muste be 'dict' or 'BaseAction'."
                )

            # TODO implement how the menu is created and debug
            # TODO include the menu drawing and update in the game manager

    def draw(self):
        """Draw the actions gui on the main display."""
        self.UI_MANAGER.draw_ui(self.GAME_MANAGER.MAIN_DISPLAY)
