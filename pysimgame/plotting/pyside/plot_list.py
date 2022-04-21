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

    def __init__(
        self, plot_list: dict[str, Plot], parent: Optional[QWidget] = None
    ):
        super().__init__(parent)

        self.buttons = {}

        self.layout = QVBoxLayout(self)

        for name, plot in plot_list.items():
            button = PlotButton(plot, name, self)
            self.buttons[name] = PlotButton

            self.layout.addWidget(button)


if __name__ == "__main__":
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
