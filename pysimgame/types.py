""" Various types used in the library. """


from typing import TYPE_CHECKING, Callable, Dict, List, Tuple, TypeVar, Union

if TYPE_CHECKING:
    from pysimgame.model import Policy
    from pysimgame.regions_display import RegionComponent

    ModelType = TypeVar("ModelType")
    # A model method must return a float and take no argument
    ModelMethod = Callable[[], float]
    # User model method is the one the user can implement having model as input
    UserModelMethod = Callable[[ModelType], float]
    Polygon = List[Tuple[int, int]]
    RegionsDict = Dict[str, RegionComponent]
    POLICY_DICT = Dict[str, List[Policy]]