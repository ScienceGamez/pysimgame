import pygame
from pygame_gui.ui_manager import UIManager

from pysdgame.game_manager import GameManager
from pysdgame.utils.dynamic_menu import UIColumnContainer


class PlotsControlManager:

    GAME_MANAGER: GameManager

    def __init__(self, GAME_MANAGER: GameManager) -> None:

        main_size = GAME_MANAGER.MAIN_DISPLAY.get_size()
        self.ui_manager = UIManager(
            main_size,
            GAME_MANAGER.PYGAME_SETTINGS["Themes"]["Statistics"],
        )

        self.ui_container = UIColumnContainer(
            pygame.Rect(
                0,
                GAME_MANAGER.MENU_OVERLAY.buttons_size,
                main_size[0]
                * GAME_MANAGER.PYGAME_SETTINGS["Display Proportions"][
                    "PlotsControl width"
                ],
                main_size[1] - GAME_MANAGER.MENU_OVERLAY.buttons_size,
            )
        )
