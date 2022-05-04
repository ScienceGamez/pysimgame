"""Contains game manager for pyside things."""
from __future__ import annotations
import sys
from typing import TYPE_CHECKING, Type
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from pysimgame.actions.actions import ActionsManager
from pysimgame.links.manager import LinksManager
from pysimgame.model import ModelManager

from pysimgame.plotting.pyside.manager import QtPlotManager
from pysimgame.regions_display import RegionsManager


from pysimgame.utils.abstract_managers import (
    AbstractGameManager,
    GameComponentManager,
)

if TYPE_CHECKING:
    from pysimgame.game_manager import GameManager


class PySideGameManager(AbstractGameManager):

    _manager_classes: list[Type[GameComponentManager]] = [
        RegionsManager,
        QtPlotManager,
        ModelManager,
        ActionsManager,
        LinksManager,
    ]

    def __init__(self) -> None:
        super().__init__()
        self.app = QApplication()

        self.timer = QTimer()

    def run_game_loop(self):
        """Main game loop handled by QT.

        TODO: The model, the plot manager and the pygame loop should run
        on separated threads.
        TODO: Use correctly the methods from abstact region component class
        (Note that they will also require proper implementation in the children)
        """

        self.logger.debug(f"[START] qt run_game_loop")

        self.timer.timeout.connect(self.game_loop)
        ms = 1000 / self.game.SETTINGS.get("FPS", 20)
        self.timer.start(ms)

        result = self.app.exec_()
        print("Qt finished: " + str(result))
        sys.exit(result)


if __name__ == "__main__":
    gm = PySideGameManager()
    gm.game = "world-3"
    gm.run_game_loop()
