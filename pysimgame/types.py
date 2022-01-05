""" Various types used in the library. """


from typing import TYPE_CHECKING, Callable, Dict, List, Tuple, TypeVar, Union

if TYPE_CHECKING:
    from pysimgame.model import Policy
    from pysimgame.regions_display import RegionComponent

    RegionName = str
    RegionsDict = Dict[RegionName, RegionComponent]

    AttributeName = str

    ModelType = TypeVar("ModelType")
    ModelsDict = Dict[RegionName, ModelType]
    # A model method must return a float and take no argument
    ModelMethod = Callable[[], float]
    # User model method is the one the user can implement having model as input
    UserModelMethod = Callable[[ModelType], float]
    Polygon = List[Tuple[int, int]]

    POLICY_DICT = Dict[str, List[Policy]]

    # Import method receives the models and return first the
    # export values and then the import values of each region
    ExportImportMethod = Callable[
        Union[
            [AttributeName, AttributeName, ModelsDict], [ModelsDict]
        ],  # Union[[str, str, ModelsDict], [ModelsDict]]
        Tuple[Dict[RegionName, float], Dict[RegionName, float]],
    ]
