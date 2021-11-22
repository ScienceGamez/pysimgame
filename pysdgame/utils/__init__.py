"""Utility module."""

import logging
from typing import Tuple


def recursive_dict_missing_values(dic_from: dict, dic_to: dict) -> dict:
    """Assign missing values from a dictonary to another.

    Assignement happens in place
    """
    for key, value in dic_from.items():
        if key not in dic_to:
            dic_to[key] = value
        elif isinstance(value, dict):
            dic_to[key] = recursive_dict_missing_values(
                dic_from[key], dic_to[key]
            )
        else:
            pass
    return dic_to


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
