"""GUI for the actions."""
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
import pygame_gui
from pygame.event import Event, event_name
from pygame_gui.elements import UIButton, UIWindow
from pygame_gui.ui_manager import UIManager
from pysdgame.actions.actions import ActionsDict, BaseAction
from pysdgame.utils import GameComponentManager
from pysdgame.utils.directories import THEME_FILENAME, THEMES_DIR
from pysdgame.utils.dynamic_menu import UIColumnContainer

if TYPE_CHECKING:
    from .actions import ActionsManager

import logging

from pysdgame.utils.logging import register_logger

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
register_logger(logger)


class ActionsGUIManager(GameComponentManager):
    UI_MANAGER: UIManager
    CONTAINER: UIColumnContainer
    ACTIONS_MANAGER: ActionsManager
    _current_actions_dict: ActionsDict

    def prepare(self):
        # Create a ui manager for this component
        display_size = self.GAME_MANAGER.MAIN_DISPLAY.get_size()
        self.UI_MANAGER = UIManager(
            display_size,
            self.GAME.SETTINGS["Themes"].get("actions", "default"),
        )
        window = UIWindow(
            rect=pygame.Rect(100, 100, 500, 500),
            manager=self.UI_MANAGER,
            window_display_title="Actions",
            resizable=True,
        )
        self.CONTAINER = UIColumnContainer(
            window.window_element_container.get_relative_rect(),
            manager=self.UI_MANAGER,
            container=window.window_element_container,
            parent_element=window,
        )

    def connect(self):
        """Connect to the actions."""
        self.ACTIONS_MANAGER = self.GAME_MANAGER.ACTIONS_MANAGER
        self._current_actions_dict = self.ACTIONS_MANAGER.actions
        self._create_actions_menu(self.ACTIONS_MANAGER.actions)

    def _update_for_new_dict(self, new_dict: ActionsDict):
        """Update the actions gui for the new actions dict."""
        if new_dict == self._current_actions_dict:
            # No update
            return
        self._current_actions_dict = new_dict
        self._create_actions_menu(new_dict)
        # Send message that has been updated
        self.update()

    def _create_actions_menu(self, actions_dict: ActionsDict):
        """Create the buttons with the actions for the actions dict."""
        h = 40
        w = self.CONTAINER.get_relative_rect().width
        self.CONTAINER.clear()
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

            self.CONTAINER.add_row(button)

            # TODO implement how the menu is created and debug
            # TODO include the menu drawing and update in the game manager

    def process_events(self, event: Event):
        """Listen the events for this manager.

        When a button is clicked.
        """
        self.UI_MANAGER.process_events(event)
        if event.type == pygame.USEREVENT:
            if (
                event.user_type == pygame_gui.UI_BUTTON_PRESSED
                and "#action_button" in event.ui_object_id
            ):
                name = event.ui_element.text
                logger.info(
                    f"Action selected {self._current_actions_dict[name]}"
                )
            elif (
                event.user_type == pygame_gui.UI_BUTTON_PRESSED
                and "#actions_type_button" in event.ui_object_id
            ):
                name = event.ui_element.text
                logger.debug(f"Action types selected {name}")
                # Redraw the gui with the new selected action
                self._update_for_new_dict(self._current_actions_dict[name])

            else:
                logger.debug(f"Other event {event}")

    def draw(self):
        """Draw the actions gui on the main display."""
        self.UI_MANAGER.draw_ui(self.GAME_MANAGER.MAIN_DISPLAY)
