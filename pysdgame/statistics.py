from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List
import pygame
from pygame_gui import elements
from pygame_gui.elements.ui_drop_down_menu import UIDropDownMenu
from pygame_gui.ui_manager import UIManager
from pygame_gui.elements import UIButton, UILabel

if TYPE_CHECKING:
    from pysdgame.model import ModelManager
from pysdgame.utils import GameComponentManager
from pysdgame.utils.dynamic_menu import UIColumnContainer
from pysdgame.utils.logging import logger


class StatisticsDisplayManager(GameComponentManager):
    UI_MANAGER: UIManager
    MODEL_MANAGER: ModelManager
    CONTAINER: UIColumnContainer

    buttons: Dict[str, UIButton]
    labels: Dict[str, UIButton]

    def prepare(self):
        main_size = self.GAME_MANAGER.MAIN_DISPLAY.get_size()
        logger.info(f"Game settings {self.GAME.SETTINGS}")
        self.UI_MANAGER = UIManager(
            main_size,
            self.GAME.SETTINGS["Themes"].get("Statistics", None),
        )

        self.CONTAINER = UIColumnContainer(
            pygame.Rect(
                0,
                60,
                main_size[0] * 0.2,
                main_size[1] - 60,
            ),
            self.UI_MANAGER,
        )
        regions = list(self.GAME.REGIONS_DICT.keys())
        container_size = self.CONTAINER.get_container().get_size()
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
        self.buttons = {}
        self.labels = {}

    def connect(self):
        self.MODEL_MANAGER = self.GAME_MANAGER.MODEL_MANAGER

        elements = self.MODEL_MANAGER.capture_elements

        for element in elements:
            self._create_line(element)

        self.listen_to_update(self.MODEL_MANAGER, self._update_stats)

    def _create_line(self, name: str):
        """Create a line in the column container with the stat."""
        w, h = self.CONTAINER.get_container().get_size()
        h = (h - self.REGIONS_HEIGTH) / len(
            self.MODEL_MANAGER.capture_elements
        )
        button = UIButton(
            pygame.Rect(0, 0, w * 0.7, h),
            name,
            self.UI_MANAGER,
            container=self.CONTAINER,
        )
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
