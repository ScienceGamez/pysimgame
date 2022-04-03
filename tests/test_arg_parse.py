import io
from pathlib import Path
import sys
import unittest
import pysimgame.arg_parse

from pysimgame.arg_parse import read_parsed_args
from pysimgame.game import Game
from pysimgame.utils.directories import TEST_DIR


def parsing_output(*args: str) -> str:
    """Return what was print in the terminal."""


class TestParseInputs(unittest.TestCase):
    stdout: io.StringIO

    def setUp(self):
        self.parser = pysimgame.arg_parse.create_parser()

        # Redirect the print outputs to
        self.old_stdout = sys.stdout
        sys.stdout = self.stdout = io.StringIO()

    def tearDown(self) -> None:
        sys.stdout = self.old_stdout

    def test_output_redirected(self):
        print("a")
        self.assertEqual(self.stdout.getvalue(), "a" + "\n")

    def test_2nd_output_redirected(self):
        print("aasdf")
        self.assertEqual(self.stdout.getvalue(), "aasdf" + "\n")

    def test_help(self):
        try:
            args = self.parser.parse_args(["--help"])
        except SystemExit as exit:
            # Help with return a system exit error
            pass
        self.assertEqual(self.parser.format_help(), self.stdout.getvalue())

    def test_help2(self):
        try:
            args = self.parser.parse_args(["-h"])
        except SystemExit as exit:
            # Help with return a system exit error
            pass
        self.assertEqual(self.parser.format_help(), self.stdout.getvalue())

    def test_list_test_games(self):
        """Read the game from the test directory."""
        test_dir_listgames = Path(TEST_DIR, "test_dir_listgames")
        args = self.parser.parse_args(
            ["--list", "--dir", str(test_dir_listgames)]
        )
        self.assertEqual(args.dir, str(test_dir_listgames))
        try:
            read_parsed_args(args)
        except SystemExit as se:
            self.assertEqual(se.code, 0)

        lines = self.stdout.getvalue().splitlines()
        self.assertGreater(len(lines), 0)
        for line, game in zip(lines, ["a", "b"]):
            self.assertEqual(
                line, str(Game(game, game_dir=test_dir_listgames))
            )

    def test_list_games(self):
        """Read the game from the test directory."""

        args = self.parser.parse_args(["--list"])
        try:
            read_parsed_args(args)
        except SystemExit as se:
            self.assertEqual(se.code, 0)

        lines = self.stdout.getvalue().splitlines()
        self.assertGreater(len(lines), 0)


if __name__ == "__main__":
    unittest.main()
