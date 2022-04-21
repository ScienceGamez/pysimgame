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

    def __init__(self, GAME_MANAGER: AbstractGameManager) -> None:
        super().__init__(GAME_MANAGER)

    def draw(self):
        """Draw the plot on a pysimgame canvas."""

    def register_plot(self, plot: Plot):
        """Register new plots.

        For efficiency, this uses only :py:class:`MplPlot`.
        """

        return super().register_plot(plot)


if __name__ == "__main__":

    manager = QtPlotManager(FakeGameManager())
    app = QApplication(sys.argv)

    window = PlotsList(
        {
            "a": FakePlot("a"),
            "d": FakePlot("b"),
            "e": FakePlot("c"),
        }
    )
    window.show()
    window.resize(440, 300)

    sys.exit(app.exec())
