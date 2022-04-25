import pandas as pd

from pysimgame.game import FakeGame
from pysimgame.model import AbstractModelManager
from pysimgame.utils.abstract_managers import AbstractGameManager


class FakeModelManager(AbstractModelManager):
    """A fake model manager."""

    data = pd.DataFrame({
        ('a', 'b'): [1, 2, 3]
    })
    

    def connect(self):
        pass

    def prepare(self):
        pass

class FakeGameManager(AbstractGameManager):
    """A fake game mangaer that can be used for test purposes."""

    def __init__(self) -> None:
        super().__init__()
        self.GAME = FakeGame()

        self.MODEL_MANAGER = FakeModelManager(self)

    def connect(self):
        pass

    def prepare(self):
        pass


