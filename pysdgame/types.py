""" Various types used in the library. """
from __future__ import annotations
import pathlib
from typing import Dict, List, Tuple, Union

from pysdgame.regions_display import RegionComponent

Polygon = List[Tuple[int, int]]
RegionsDict = Dict[str, RegionComponent]
FilePath = Union[str, pathlib.Path]
DirPath = Union[str, pathlib.Path]
