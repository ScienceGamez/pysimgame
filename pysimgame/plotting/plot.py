from __future__ import annotations

import logging
from dataclasses import dataclass, field


from typing import TYPE_CHECKING, Callable, Dict, List, overload

import matplotlib.axes
import matplotlib.figure
import numpy as np

from pysimgame.regions_display import RegionComponent

if TYPE_CHECKING:
    from pysimgame.types import AttributeName, RegionName
    import matplotlib.artist
    import pandas as pd

    ArtistsDict = dict[str, matplotlib.artist.Artist]
    DataFrames = dict[tuple[RegionName, AttributeName], pd.Series]
    PlotFunction = Callable[[matplotlib.axes.Axes, DataFrames], ArtistsDict]
    BlitFunction = Callable[[ArtistsDict, DataFrames], None]


@dataclass
class PlotLine:
    """A line that will be plotted using the matplotlib plot function.

    Any kwargs that should be passed to plt.plot
    can be done using  kwargs ={}.
    """

    region: str
    attribute: str | List[str]
    kwargs: dict = field(default_factory=dict)
    share_y: bool = True
    y_lims: list = None


def plot(
    figure: matplotlib.figure.Figure,
    ax: matplotlib.axes.Axes,
    data: Dict[RegionName, Dict[AttributeName, np.ndarray]],
    *plot_lines: PlotLine,
):
    for line in plot_lines:
        ax.plot(data[line.region][line.attribute])


class Plot:
    """Represent a plot for pysimgame."""

    name: str

    def __init__(self, name: str) -> None:
        """Create a plot and register it in the plot manager."""

        if not isinstance(name, str):
            logging.getLogger(__name__).error("Plot name must be str.")
        self.name = name

        from .base import _PLOT_MANAGER

        _PLOT_MANAGER.register_plot(self)


class LinePlot(Plot):
    """Plot simple lines.

    You can specify either :py:class:`PlotLine` which correspond
    to a region and an attribute, or specify the name of the
    regions you want to plot and the name of the attributes,
    to plot all the combinations between them.
    """

    name: str
    plot_lines: List[PlotLine]
    plot_method: Callable

    # @overload
    # def __init__(self, *args: PlotLine) -> None:
    #     ...

    # @overload
    # def __init__(
    #     self,
    #     regions: RegionName | List[RegionName],
    #     attributes: AttributeName | List[AttributeName],
    #     *args: PlotLine,
    # ) -> None:
    #     ...

    def __init__(
        self,
        name: str,
        *args: PlotLine,
        regions: RegionName | List[RegionName] = None,
        attributes: AttributeName | List[AttributeName] = None,
    ) -> None:
        """Create a plot object."""
        super().__init__(name)
        from .base import _PLOT_MANAGER

        game = _PLOT_MANAGER.GAME
        if regions is None:
            # None means all regions
            regions = (
                list(game.REGIONS_DICT.keys())
                if not args or attributes is not None
                else []
            )
        if attributes is None:
            attributes = (
                _PLOT_MANAGER.MODEL_MANAGER.capture_attributes
                if not args
                else []
            )
        if isinstance(regions, str):
            regions = [regions]
        if isinstance(attributes, str):
            attributes = [attributes]
        # Adds the lines specified by the user

        self.plot_lines = list(args) + [
            PlotLine(reg, attributes) for reg in regions
        ]


class MplPlot(Plot):
    """Customizable :py:mod:`matplotlib` compabtible Plot class.

    It is using
    `blitting <https://matplotlib.org/stable/tutorials/advanced/blitting.html>`_
    which can render plot efficiently.

    :arg name: The name of the Plot
    :arg plot_func: Specify what should be plotted at the beggining.
        This must return the artists, as a dict.
    :arg blit_func: Called at every model update, knows what to change
        in the plot.
        Usually just setting the data.
    """

    # A function receiving a dataframe with the data and returning the created artists

    plot_func: PlotFunction
    blit_func: BlitFunction

    def __init__(
        self, name: str, plot_func: PlotFunction, blit_func: BlitFunction
    ) -> None:
        super().__init__(name)
        self.plot_func = plot_func
        self.blit_func = blit_func


class FakePlot(Plot):
    """This is a fake of the Plot class that can be used for tests."""

    def __init__(
        self,
        name: str,
        *args: PlotLine,
        regions: RegionName | List[RegionName] = None,
        attributes: AttributeName | List[AttributeName] = None,
    ) -> None:
        super().__init__(name)
