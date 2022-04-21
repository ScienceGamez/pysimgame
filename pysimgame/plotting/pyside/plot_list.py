import sys
from textwrap import wrap
from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QApplication,
    QWidget,
    QVBoxLayout,
)
from PySide6.QtCore import Signal
from functools import wraps


from pysimgame.plotting.plot import FakePlot, Plot


class PlotButton(QPushButton):
    """A special button that is used to pop a plot."""

    is_opened: bool
    plot: Plot

    @wraps(QPushButton.__init__)
    def __init__(self, plot: Plot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_opened = False
        self.plot = Plot


class PlotsList(QWidget):
    """A widget containing a list of the possible plots."""

    buttons: dict[str, PlotButton]

    open_plot: Signal = Signal(Plot)

    def __init__(
        self, plot_list: list[Plot], parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self.buttons = {}

        self.layout = QVBoxLayout(self)

        for plot in plot_list:
            button = PlotButton(plot, plot.name, self)
            self.buttons[plot.name] = PlotButton

            self.layout.addWidget(button)

            def emit_plot(checked: bool = False, plot=plot):
                self.open_plot.emit(plot)

            button.clicked.connect(emit_plot)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = PlotsList(
        [
            FakePlot("a"),
            FakePlot("b"),
            FakePlot("c"),
        ]
    )
    window.show()
    window.resize(440, 300)

    sys.exit(app.exec())
