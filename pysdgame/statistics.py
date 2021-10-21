import pygame
from pygame_gui.ui_manager import UIManager

from pysdgame.game_manager import GameManager
from pysdgame.utils.dynamic_menu import UIColumnContainer


class GraphsControlManager:

    GAME_MANAGER: GameManager

    def __init__(self, game_manager: GameManager) -> None:

        main_size = game_manager.MAIN_DISPLAY.get_size()
        self.ui_manager = UIManager(
            main_size,
            game_manager.PYGAME_SETTINGS["Themes"]["Statistics"],
        )

        self.ui_container = UIColumnContainer(
            pygame.Rect(
                0,
                game_manager.MENU_OVERLAY.buttons_size,
                main_size[0]
                * game_manager.PYGAME_SETTINGS["Display Proportions"][
                    "GraphsControl width"
                ],
                main_size[1] - game_manager.MENU_OVERLAY.buttons_size,
            )
        )
