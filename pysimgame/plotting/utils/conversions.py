from __future__ import annotations
from typing import TYPE_CHECKING, Any
from matplotlib.lines import Line2D

import pandas as pd


from ..plot import LinePlot, MplPlot


if TYPE_CHECKING:
    from pysimgame.types import AttributeName, RegionName
    from matplotlib.artist import Artist
    from matplotlib.axes import Axes
    from ..plot import (
        ArtistsDict,
        BlitFunction,
        DataFrames,
        PlotFunction,
    )


def lineplots_to_mplplots(line_plot: LinePlot) -> MplPlot:
    """Convert a :py:class:`LinePlot` to a :py:class:`MplPlot`."""


    def plot_func(
        ax: Axes, data: dict[tuple[RegionName, AttributeName], pd.Series]
    ) -> dict[str, Artist]:
        """Create the artists needed for the lines."""
        artists: dict[str, Line2D] = {}
        for line in line_plot.plot_lines:
            attr_list = [line.attribute] if isinstance(line.attribute, str) else line.attribute
            for attr in attr_list:
                # There will be only 1 artist per line
                artist[f"{line.region}|{attr}"] =  ax.plot(
                    data[(line.region, attr)]
                )[0]
               
            

        for artist in artists.values():
            artist.set_animated(True)

        return artists

    def blit_func(artists: dict[str, Line2D], data: DataFrames) -> None:
        for art_str, line in artists.items():
            # TODO: make sure | is forbidden in RegionName
            line.set_data(data[art_str.split("|", maxsplit=1)])

    return MplPlot(line_plot.name, plot_func, blit_func)
