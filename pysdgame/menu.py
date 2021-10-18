"""A class that handles the menu of the game."""
from __future__ import annotations
import pygame_gui


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pysdgame.game_manager import GameManager


class MenuOverlay:
    """Class that handles the menu of the game."""

    GAME_MANAGER: GameManager

    def __init__(self, game_manager) -> None:
        pass
