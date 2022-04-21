"""A plot manager using basic matplotlib backends."""
import sys
from typing import TYPE_CHECKING

import matplotlib
from pysimgame.utils.abstract_managers import AbstractGameManager

from pysimgame.utils.fake import FakeGameManager

from pysimgame.plotting.plot import FakePlot, MplPlot, Plot
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


class MplCanvas(FigureCanvasQTAgg):
    ax: matplotlib.axes.Axes

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.ax = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class QtPlotManager(AbstractPlotsManager):
    """Manager using standard qt backend."""

    canvas = dict[Plot, MplCanvas]

    # This store only mpl plots
    plots: list[MplPlot]

    plot_list: PlotsList

    def __init__(self, GAME_MANAGER: AbstractGameManager) -> None:
        super().__init__(GAME_MANAGER)

    def prepare(self):
        pass

    def show_plots_list(self):
        if not hasattr(self, "plot_list"):
            # Create the plot list if was not created
            self.plot_list = PlotsList(self.plots)
            self.plot_list.open_plot.connect(self.register_plot)
            self.plot_list.show()
            # TODO: define the size
            self.plot_list.resize(440, 300)

        self.plot_list.setVisible(True)

    def draw(self):
        """Draw the plot on a pysimgame canvas."""

    def register_plot(self, plot: Plot):
        """Register new plots.

        For efficiency, this uses only :py:class:`MplPlot`.
        """
        self.logger.warn(f"registered {plot}")
        return super().register_plot(plot)


if __name__ == "__main__":

    app = QApplication()

    manager = QtPlotManager(FakeGameManager())

    FakePlot("a")
    FakePlot("b")
    FakePlot("c")

    manager.show_plots_list()

    sys.exit(app.exec())
