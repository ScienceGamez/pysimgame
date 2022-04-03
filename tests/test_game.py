from pathlib import Path
import unittest

from pysimgame.game import Game, GameNotFoundError, list_available_games
from pysimgame.utils.directories import EXAMPLES_DIR, TEST_DIR


class TestGameCreation(unittest.TestCase):
    def test_specifiying_dir(self):
        game = Game("game_0", game_dir=Path(TEST_DIR, "test_games"))

    def test_doesnot_exists_raise_gamenotfounderror(self):
        self.assertRaises(
            GameNotFoundError, Game, "game_not_found_error_does_not_exist"
        )


class TestAvailableGames(unittest.TestCase):
    def test_read_dir(self):
        games = list_available_games(Path(TEST_DIR, "test_dir_listgames"))
        for game in games:
            self.assertIn(game.NAME, ["a", "b"])


if __name__ == "__main__":
    unittest.main()
