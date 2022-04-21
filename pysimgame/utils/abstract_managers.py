"""Contain some abstract managers.

Help to solve some dependency issues with some managers.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, Type


if TYPE_CHECKING:
    import pygame
    from pysimgame.game import Game
    from pysimgame.actions.actions import ActionsManager
    from pysimgame.menu import MenuOverlayManager
    from pysimgame.model import ModelManager
    from pysimgame.plotting.base import AbstractPlotsManager
    from pysimgame.regions_display import RegionsManager
    from pysimgame.statistics import StatisticsDisplayManager

from pysimgame.utils import GameComponentManager


_GAME_MANAGER: AbstractGameManager = None


class AbstractGameManager(GameComponentManager):
    """An abstract game manager that contain the minimum required.

    All game managers should inherit from this one.
    The main idea is that only the
    :py:attr`_manager_classes` should be replaced by the components.
    """

    # Components managers
    MANAGERS: dict[str, GameComponentManager]

    # Set the manager classes this main manager is using
    _manager_classes: list[Type[GameComponentManager]]

    # Mandatory managers
    MODEL_MANAGER: ModelManager
    PLOTS_MANAGER: AbstractPlotsManager
    STATISTICS_MANAGER: StatisticsDisplayManager
    ACTIONS_MANAGER: ActionsManager
    REGIONS_MANAGER: RegionsManager
    MENU_OVERLAY: MenuOverlayManager

    # Stores the time
    CLOCK: pygame.time.Clock

    GAME: Game

    def __init__(self) -> None:
        """Override the main :py:class:`GameManager` is the main organizer."""
        self._set_logger()
        global _GAME_MANAGER
        if _GAME_MANAGER is None:
            _GAME_MANAGER = self
        self.MANAGERS = {}
