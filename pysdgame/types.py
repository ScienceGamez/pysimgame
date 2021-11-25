""" Various types used in the library. """


from typing import Dict, List, Tuple, Union


from pysdgame.regions_display import RegionComponent

Polygon = List[Tuple[int, int]]
RegionsDict = Dict[str, RegionComponent]
