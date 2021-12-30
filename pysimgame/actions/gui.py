"""GUI for the actions."""
from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
import pygame_gui
import pysimgame
from pygame.event import Event, EventType, event_name
from pygame_gui.elements import UIButton, UIHorizontalSlider, UILabel, UIWindow
from pygame_gui.ui_manager import UIManager
from pysimgame.actions.actions import ActionsDict, BaseAction, Budget, Policy
from pysimgame.utils import GameComponentManager
from pysimgame.utils.directories import THEME_FILENAME, THEMES_DIR
from pysimgame.utils.dynamic_menu import UIColumnContainer

if TYPE_CHECKING:
    from .actions import ActionsManager
    from pysimgame.model import ModelManager
    from pysimgame.regions_display import RegionsManager

import logging

from pysimgame.utils.logging import register_logger

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# register_logger(logger)


class ActionsGUIManager(GameComponentManager):
    UI_MANAGER: UIManager
    CONTAINER: UIColumnContainer
    ACTIONS_MANAGER: ActionsManager
    REGIONS_MANAGER: RegionsManager
    MODEL_MANAGER: ModelManager
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
        self.REGIONS_MANAGER = self.GAME_MANAGER.REGIONS_MANAGER
        self.MODEL_MANAGER = self.GAME_MANAGER.MODEL_MANAGER
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
                self.CONTAINER.add_row(button)
            elif isinstance(action, Policy):
                # Create a button to trigger
                button = UIButton(
                    relative_rect=pygame.Rect(0, 0, w, h),
                    text=name,
                    manager=self.UI_MANAGER,
                    container=self.CONTAINER,
                    object_id="#action_button",
                )
                self.CONTAINER.add_row(button)
            elif isinstance(action, Budget):
                # A budget needs a slider to change the value and a value

                # First get the start valuue of the action variable
                start_value = getattr(
                    self.MODEL_MANAGER[
                        self.REGIONS_MANAGER.selected_region
                    ].components,
                    action.variable,
                )()
                # A slider for value selection
                slider = UIHorizontalSlider(
                    relative_rect=pygame.Rect(0, h / 2, w, h / 2),
                    start_value=start_value,
                    value_range=(action.get_min(), action.get_max()),
                    manager=self.UI_MANAGER,
                    container=self.CONTAINER,
                    object_id="#budget_slider",
                )
                lab_w = w / 3
                variable_label = UILabel(
                    relative_rect=pygame.Rect(
                        (w - lab_w) / 2, 0, lab_w, h / 2
                    ),
                    text=f"{action.variable}: ",
                    manager=self.UI_MANAGER,
                    container=self.CONTAINER,
                    object_id="#budget_label",
                )
                value_label = UILabel(
                    relative_rect=pygame.Rect(
                        (w - lab_w) / 2 + lab_w, 0, lab_w, h / 2
                    ),
                    text=f"{start_value}",
                    manager=self.UI_MANAGER,
                    container=self.CONTAINER,
                    object_id="#budget_label",
                )
                self.CONTAINER.add_row(slider, variable_label, value_label)
                # Attribute the label so we can us it later
                slider.label = value_label
                slider.action = action
            else:
                raise TypeError(
                    f"Invalid type in ActionsDict : {type(action)}."
                    "Muste be 'dict' or 'BaseAction'."
                )

            # TODO implement how the menu is created and debug
            # TODO include the menu drawing and update in the game manager

    def process_events(self, event: Event):
        """Listen the events for this manager.

        When a button is clicked.
        """
        self.UI_MANAGER.process_events(event)
        match event:
            case EventType(
                type=pygame.USEREVENT, user_type=pygame_gui.UI_BUTTON_PRESSED
            ):
                name = event.ui_element.text
                if "#action_button" in event.ui_object_id:
                    # Activate the action
                    action = self._current_actions_dict[name]
                    if action.activated:
                        action.deactivate()
                    else:
                        action.activate()
                    self.ACTIONS_MANAGER.post_event(action)

                    logger.info(
                        f"Action selected {self._current_actions_dict[name]}"
                    )
                elif "#actions_type_button" in event.ui_object_id:

                    logger.debug(f"Action types selected {name}")
                    # Redraw the gui with the new selected action
                    self._update_for_new_dict(self._current_actions_dict[name])
                else:
                    logger.debug(f"Other event {event}")
            case EventType(
                type=pygame.USEREVENT,
                user_type=pygame_gui.UI_HORIZONTAL_SLIDER_MOVED,
            ):
                if "#budget_slider" in event.ui_object_id:
                    label: UILabel = event.ui_element.label
                    label.set_text(f"{event.ui_element.get_current_value()}")
                    # Send event changed
                    event.ui_element.action.value = event.value
                    self.ACTIONS_MANAGER.post_event(event.ui_element.action)

            case EventType(type=pysimgame.ActionUsed):
                print(pysimgame.ActionUsed)
                logger.info(f"ActionUsed {event}")
            case _:
                pass

    def draw(self):
        """Draw the actions gui on the main display."""
        self.UI_MANAGER.draw_ui(self.GAME_MANAGER.MAIN_DISPLAY)
