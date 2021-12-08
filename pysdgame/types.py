""" Various types used in the library. """


from typing import Dict, List, Tuple, Union
from pysdgame.model import Policy
from pysdgame.regions_display import RegionComponent

Polygon = List[Tuple[int, int]]
RegionsDict = Dict[str, RegionComponent]
POLICY_DICT = Dict[str, List[Policy]]
