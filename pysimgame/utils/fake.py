from pysimgame.game import FakeGame
from pysimgame.utils.abstract_managers import AbstractGameManager


class FakeGameManager(AbstractGameManager):
    """A fake game mangaer that can be used for test purposes."""

    def __init__(self) -> None:
        super().__init__()
        self.GAME = FakeGame()

    def connect(self):
        pass

    def prepare(self):
        pass
