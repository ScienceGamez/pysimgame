"""Utility module."""
from __future__ import annotations

import pathlib

from typing import TYPE_CHECKING, Callable, Tuple


from .logging import logging, register_logger

if TYPE_CHECKING:
    from pysimgame.game_manager import Game


def close_points(
    point1: Tuple[int, int], point2: Tuple[int, int], PIXEL_THRESHOLD: int = 10
) -> bool:
    """Return True if the points are close enough else False.

    Use Manatthan distance.
    """
    return (
        abs(point1[0] - point2[0]) + abs(point1[1] - point2[1])
        < PIXEL_THRESHOLD
    )


class _HintDisplay:
    """Display hints for the user on his screen.

    Currently only prints in terminal but could put things on screen
    in the future.
    """

    def __main__(self):
        """Create the hint displayer."""
        # TODO implement this to have proper on screan display
        logger = logging.getLogger(__name__)
        pass

    def show(self, text: str):
        """Show the text as hint."""
        print(text)


HINT_DISPLAY = _HintDisplay()


def create_modding_file(game: Game | str):
    """Create the modding helper file."""
    import json

    if isinstance(game, str):
        from pysimgame.game_manager import Game

        game = Game(game)
    file = pathlib.Path(game.GAME_DIR, "modding_help.json")

    dic = {
        "Regions": [k for k in game.REGIONS_DICT.keys()],
        "Attributes": [m for m in game.load_model()._namespace.values()],
    }

    with file.open("w") as f:
        json.dump(dic, f, indent=2)
