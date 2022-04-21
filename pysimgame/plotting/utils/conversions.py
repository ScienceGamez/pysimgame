from typing import TYPE_CHECKING, Any
from matplotlib.lines import Line2D

import pandas as pd

from ..plot import (
    ArtistsDict,
    BlitFunction,
    DataFrames,
    LinePlot,
    MplPlot,
    PlotFunction,
)

if TYPE_CHECKING:
    from pysimgame.types import AttributeName, RegionName
    from matplotlib.artist import Artist
    from matplotlib.axes import Axes


def lineplots_to_mplplots(line_plot: LinePlot) -> MplPlot:
    """Convert a :py:class:`LinePlot` to a :py:class:`MplPlot`."""
    PlotFunction
    BlitFunction
    ArtistsDict
    DataFrames

    def plot_func(
        ax: Axes, data: dict[tuple[RegionName, AttributeName], pd.Series]
    ) -> dict[str, Artist]:
        """Create the artists needed for the lines."""
        artists: dict[str, Line2D] = {
            # There will be only 1 artist per line
            f"{line.region}|{line.attribute}": ax.plot(
                data[(line.region, line.attribute)]
            )[0]
            for line in line_plot.plot_lines
        }

        for artist in artists.values():
            artist.set_animated(True)

        return artists

    def blit_func(artists: dict[str, Line2D], data: DataFrames) -> None:
        for art_str, line in artists.items():
            # TODO: make sure | is forbidden in RegionName
            line.set_data(data[art_str.split("|", maxsplit=1)])

    return MplPlot(line_plot.name, plot_func, blit_func)
