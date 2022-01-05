from collections import namedtuple
from typing import TYPE_CHECKING, List, overload

if TYPE_CHECKING:
    from pysimgame.types import AttributeName, RegionName

PlotLine = namedtuple("PlotLine", ["attribute", "region"])


class Plot:

    plot_lines: List[PlotLine]

    @overload
    def __init__(self, *args: PlotLine) -> None:
        ...

    @overload
    def __init__(
        self,
        regions: RegionName | List[RegionName],
        attributes: AttributeName | List[AttributeName],
        *args: PlotLine,
    ) -> None:
        ...

    def __init__(self, *args) -> None:
        pass


p = Plot()
