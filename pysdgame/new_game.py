"""Module for creating a new game from user choice."""
import pathlib

from .utils.directories import PYSDGAME_DIR


def error_popup(msg: str):
    return


def check_game_name(name: str) -> None:
    # Check that it already exist
    dir = pathlib.Path(PYSDGAME_DIR)
    if name in dir.iterdir():
        error_popup("Name {} is already taken".format(name))


def from_local_file(
    name: str,
    model_file: pathlib.Path,
    theme_file: pathlib.Path = None,
) -> None:
    return
