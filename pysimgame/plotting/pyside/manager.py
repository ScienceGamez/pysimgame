"""A plot manager using basic matplotlib backends."""
from __future__ import annotations
import sys
from typing import TYPE_CHECKING

import matplotlib
from pysimgame.plotting.utils.conversions import lineplots_to_mplplots
from pysimgame.utils.abstract_managers import AbstractGameManager

from pysimgame.utils.fake import FakeGameManager

from pysimgame.plotting.plot import  FakePlot, LinePlot, MplPlot, Plot
from pysimgame.plotting.base import AbstractPlotsManager
from pysimgame.plotting.pyside.plot_list import PlotsList, PlotButton

from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QApplication,
    QWidget,
    QVBoxLayout,
)


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

if TYPE_CHECKING:
    import matplotlib.axes
    from pysimgame.plotting.plot import ArtistsDict


class MplCanvas(FigureCanvasQTAgg):
    ax: matplotlib.axes.Axes

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class QtPlotManager(AbstractPlotsManager):
    """Manager using standard qt backend."""

    canvas : dict[MplPlot, MplCanvas]
    artists: dict[MplPlot, ArtistsDict]

    # This store only mpl plots
    plots: list[MplPlot]

    plot_list: PlotsList

    # Helpers
    _opens_plots: list[Plot]  # Tracks open plots

    def __init__(self, GAME_MANAGER: AbstractGameManager) -> None:
        super().__init__(GAME_MANAGER)

    def prepare(self):
        self._opens_plots = []
        self.canvas = {}
        self.artists = {}
    
    def connect(self):
        self.data = self.GAME_MANAGER.MODEL_MANAGER.data

    def register_plot(self, plot: Plot):
        """Register new plots.

        For efficiency, this uses only :py:class:`MplPlot`.
        """
        self.logger.info(f"registered {plot}")

        # Transfrom some type of plots into other kinds
        match plot:
            case LinePlot():
                print("plotlist", plot)
                lineplots_to_mplplots(plot)
                return # PLot is registered on creation inside the converter
            case MplPlot():
                print("mpl", plot)
            case Plot():
                print("plot", plot)

        return super().register_plot(plot)

    def show_plots_list(self):
        if not hasattr(self, "plot_list"):
            # Create the plot list if was not created
            self.plot_list = PlotsList(self.plots)
            self.plot_list.open_plot.connect(self.open_plot)
            self.plot_list.show()

        self.plot_list.setVisible(True)

    def open_plot(self, plot: MplPlot):
        """Open the plot for the player to see it."""
        # Add a new canvas
        if plot in self.canvas:
            self.logger.debug(f"{plot} already in canvas.")
            self.canvas[plot]
            return
        self.canvas[plot] = MplCanvas()

        ax = self.canvas[plot].ax

        self.artists[plot] = plot.plot_func(ax, self.data)

    def draw(self):
        """Updates the plots."""
        # Automatically called by the abstract
        for plot, canvas in self.canvas.items():
            plot.blit_func(self.artists[plot], self.data)
            canvas.draw()


if __name__ == "__main__":

    app = QApplication()

    game_manager = FakeGameManager()
    manager = QtPlotManager(game_manager)
    manager.prepare()
    manager.connect()

    FakePlot("a")
    FakePlot("b")
    FakePlot("c")

    LinePlot("b", attributes=["a"])

    manager.show_plots_list()

    app.exec()
