"""Modifiers allow to change a single attribute for a region."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pysimgame.types import ModelMethod, ModelType, RegionName


def modifiy(
    region: RegionName, attribute: str, new_func: ModelMethod | int | float
):
    """Modify a single attribute for a specific region."""
    from .manager import _LINKS_MANAGER

    if isinstance(new_func, (int, float)):
        a = new_func  # copy the int float value to a variable

        def _func():
            return a

    elif callable(new_func):
        _func = new_func
    else:
        _LINKS_MANAGER.logger.error(
            f"{new_func} must be int, float or a function. "
            f"Not {type(new_func)}."
        )
    _LINKS_MANAGER.MODEL_MANAGER.link_modify(region, attribute, _func)
