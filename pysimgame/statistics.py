from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List
import pygame
from pygame_gui import elements
import pygame_gui
from pygame_gui.elements.ui_drop_down_menu import UIDropDownMenu
from pygame_gui.ui_manager import UIManager
from pygame_gui.elements import UIButton, UILabel, UITextBox

if TYPE_CHECKING:
    from pysimgame.model import ModelManager
from pysimgame.utils import GameComponentManager
from pysimgame.utils.dynamic_menu import UIColumnContainer
from pysimgame.utils.logging import logger


class StatisticsDisplayManager(GameComponentManager):
    UI_MANAGER: UIManager
    MODEL_MANAGER: ModelManager
    CONTAINER: UIColumnContainer

    buttons: Dict[str, UIButton]
    labels: Dict[str, UIButton]

    def prepare(self):
        main_size = self.GAME_MANAGER.MAIN_DISPLAY.get_size()
        logger.debug(f"Game settings {self.GAME.SETTINGS}")
        self.UI_MANAGER = UIManager(
            main_size,
            self.GAME.SETTINGS["Themes"].get("Statistics", None),
        )
        logger.debug(f"MAINT diplay size: {main_size}")
        colomun_width = 0.25
        menu_height = 0.07
        self.CONTAINER = UIColumnContainer(
            pygame.Rect(
                main_size[0] * (1.0 - colomun_width),
                main_size[1] * menu_height,
                main_size[0] * colomun_width,
                main_size[1] * (1 - menu_height),
            ),
            self.UI_MANAGER,
            object_id="#StatisticsContainer",
        )
        regions = list(self.GAME.REGIONS_DICT.keys())
        container_size = self.CONTAINER.get_container().get_size()
        logger.debug(f"container size: {container_size}")
        self.REGIONS_HEIGTH = 40
        self.drop_down = UIDropDownMenu(
            regions,
            starting_option=regions[0],
            relative_rect=pygame.Rect(
                0, 0, container_size[0], self.REGIONS_HEIGTH
            ),
            manager=self.UI_MANAGER,
            container=self.CONTAINER,
        )
        # Calculate the space that will be left for the elements
        self._vertical_available_space = (
            container_size[1] - self.REGIONS_HEIGTH
        )
        self.CONTAINER.add_row(self.drop_down)
        # Empty dict to store all UI components
        self.buttons = {}
        self.labels = {}

        self._hidden = False

    def connect(self):
        self.MODEL_MANAGER = self.GAME_MANAGER.MODEL_MANAGER

        elements = self.MODEL_MANAGER.capture_elements

        for element in elements:
            self._create_line(element)

        self.listen_to_update(self.MODEL_MANAGER, self._update_stats)

    def hide(self):
        self.CONTAINER.hide()
        self._hidden = True

    def show(self):
        self.CONTAINER.show()
        self._hidden = False

    def _create_line(self, name: str):
        """Create a line in the column container with the stat."""
        w, h = self.CONTAINER.get_container().get_size()
        logger.debug(f"contaner size: {w,h}")
        h = self._vertical_available_space / len(
            self.MODEL_MANAGER.capture_elements
        )
        logger.debug(f"height: {h}")
        doc = self.MODEL_MANAGER.doc
        button = UIButton(
            pygame.Rect(0, 0, w * 0.7, h),
            text=doc[name].get("Real Name"),
            manager=self.UI_MANAGER,
            container=self.CONTAINER,
            allow_double_clicks=True,
            tool_tip_text=str(self.MODEL_MANAGER.doc[name]),
        )
        # Set a special attribute to buttons, recalling the variable
        value_label = UILabel(
            pygame.Rect(w * 0.7, 0, w * 0.3, h),
            text="",
            manager=self.UI_MANAGER,
            container=self.CONTAINER,
        )

        self.buttons[name] = button
        self.labels[name] = value_label
        self.CONTAINER.add_row(button, value_label)

    def _update_stats(self) -> None:
        # Get the model of the current region
        model = self.MODEL_MANAGER.models[self.drop_down.selected_option]
        for element, label in self.labels.items():
            label.set_text("{:1.3f}".format(model[element]))

    def process_events(self, event: pygame.event.Event):
        self.UI_MANAGER.process_events(event)

        if (
            event.type == pygame.USEREVENT
            and event.user_type == pygame_gui.UI_BUTTON_DOUBLE_CLICKED
            and event.ui_element in self.buttons.values()
        ):
            logger.debug("Got ")
            pass
