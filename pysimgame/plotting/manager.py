"""plots models for ills fate.

The Graph manager handles plots creations and transfer of data from
the model.
Different plots window can be created:
    - Parameters evolution graph. Can plot the parameters of a model
        though time.
    - Regions evolution graph. Plot the same parameter across regions.
    - Regions comparison heatmap.
"""
from __future__ import annotations

import logging
import pathlib
import threading
import time
from importlib.machinery import SourceFileLoader
from typing import TYPE_CHECKING, Dict, List, Tuple, Type

import numpy as np
import pandas
import pygame
import pygame_gui
import pysimgame
from matplotlib.lines import Line2D
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.ui_manager import UIManager
from pygame_matplotlib import pygame_color_to_plt
from pygame_matplotlib.backend_pygame import FigureSurface
from pygame_matplotlib.gui_window import UIPlotWindow
from pysimgame.model import ModelManager
from pysimgame.utils import GameComponentManager
from pysimgame.utils.logging import logger
from pysimgame.utils.strings import beautify_parameter_name

from ..utils.maths import normalize

if TYPE_CHECKING:
    from ..game_manager import GameManager
    from .plot import Plot
    import matplotlib
    import matplotlib.axes
    import matplotlib.artist
    from pysimgame.types import AttributeName, RegionName

import matplotlib.pyplot as plt

COLORS_LIST = ("red", "blue", "green", "orange")

REGION_COLORS = {""}

Region: Type[str] = str

_PLOT_MANAGER: PlotsManager


class PysgamePlotWindow(UIPlotWindow):
    """Attributes for a pysimgame plot.

    This is not used.
    TODO: See if this could be useful somehow.
    """

    # Stores the info on what to plot
    regions: List[str]
    attributes: List[str]
    _regions: List[str]
    _attributes: List[str]
    # Stores the attributes of the figure
    figure: FigureSurface
    ax: matplotlib.axes.Axes
    artists: List[matplotlib.artist.Artist]

    @property
    def regions(self) -> List[str]:
        return self._regions

    @regions.setter
    def regions(self, regions: List[str]):
        if regions is None:
            regions = []
        self._regions = list(regions).copy()

    @property
    def attributes(self) -> List[str]:
        return self._attributes

    @attributes.setter
    def attributes(self, attributes: List[str]):
        if attributes is None:
            attributes = []
        self._attributes = list(attributes).copy()

    def __str__(self) -> str:
        return "Plot window: \n \t Regions {} \t attributes: {}".format(
            self.regions, self.attributes
        )


class PlotsManager(GameComponentManager):
    """A manager for plots.

    Register all the plots that were created and that are now active.
    Updates the at every step with the new data.


    Notes on the implementation.
    The plotting process runs on separated threads, as it takes a bit of
    time, so the main process can run without needing to wait for the plots.
    """

    ui_plot_windows: Dict[str, UIPlotWindow]
    GAME_MANAGER: GameManager
    MODEL_MANAGER: ModelManager
    axes: Dict[str, List[matplotlib.axes.Axes]]
    lines: Dict[str, List[Line2D]]
    _connected: bool = False
    region_colors: Dict[str, Tuple[float, float, float, float]]

    plots: Dict[str, Plot]

    _menu_button: UIButton
    _plot_list_buttons: List[UIButton]

    _menu_button_position: Tuple[int, int]

    _content_thread: threading.Thread
    _surface_thread: threading.Thread
    _figsurface_locks: Dict[str, threading.Lock]
    _last_time: float

    # Initialization Methods #

    def prepare(self):
        """Prepare the graph manager."""

        self.ui_plot_windows = {}
        self.axes = {}
        self.lines = {}
        self.previous_serie = None
        self._plot_list_buttons = []
        self.plots = {}
        self._content_thread = None
        self._surface_thread = None
        self._figsurface_locks = {}
        self._last_time = time.time()

        self._read_regions_colors()
        # Manager for the standard UI stuff
        self.UI_MANAGER = self.GAME_MANAGER.UI_MANAGER
        # Manager for showing the plots
        # This should not be called by the main thread !
        # So we make it private
        self._UI_MANAGER = UIManager(
            self.GAME_MANAGER.MAIN_DISPLAY.get_size(),
        )

        global _PLOT_MANAGER
        _PLOT_MANAGER = self

    def _read_regions_colors(self):
        self.region_colors = {
            name: pygame_color_to_plt(cmpnt.color)
            for name, cmpnt in self.GAME_MANAGER.game.REGIONS_DICT.items()
            if name is not None
        }
        logger.debug(f"Regions Color {self.region_colors}")

    def connect(self):
        self._connect_to_model(self.GAME_MANAGER.MODEL_MANAGER)
        self._menu_button_position = (
            self.GAME_MANAGER.MENU_OVERLAY.overlay_buttons[-1]
            .get_abs_rect()
            .bottomleft
        )

    def _connect_to_model(self, MODEL_MANAGER: ModelManager):
        """Connect the plots display to the models."""
        self.model_outputs = MODEL_MANAGER.outputs
        self.MODEL_MANAGER = MODEL_MANAGER

        # Create a df containing regions and alements
        self.df_keys = self.model_outputs.keys().to_frame(index=False)

        # Load the plots
        plots_dir = pathlib.Path(self.GAME.GAME_DIR, "plots")
        if not plots_dir.exists():
            plots_dir.mkdir()
        plots_files = list(plots_dir.rglob("*.py"))
        # Read what is in the files
        for file in plots_files:
            SourceFileLoader("", str(file)).load_module()

        logger.debug(f"Files: {plots_files}")
        # Register connected
        self._connected = True

    # Adding plots methods

    def get_a_rect(self) -> pygame.Rect:
        """Return a rect from a nice place in the main window.

        TODO: make it a nice place for real...
        """
        return pygame.Rect(0, 0, 300, 300)

    def add_plot(self, name: str, plot: Plot):
        """Add a :py:class:`Plot` to the manager."""
        self.logger.setLevel(logging.DEBUG)
        self.logger.debug(f"Adding {plot = }")
        self.logger.debug(f"{plot.plot_lines = }")
        if name in self.plots.keys():
            # Already there
            self.logger.warn(f"{name} already in plots.")
            return
        self.plots[name] = plot
        self._figsurface_locks[name] = threading.Lock()
        self.logger.debug(f"Lock created : {self._figsurface_locks[name]}")

        if self._connected:
            self._create_plot_window(name)
        self.logger.setLevel(logging.INFO)

    def _create_plot_window(self, plot_name: str | Plot):
        """Create the plot on the window.

        Assume plot_window has regions and attributes it need to plot.
        """
        if not isinstance(plot_name, str):
            plot_name = plot_name.name
        if plot_name not in self.ui_plot_windows.keys():
            # Needs to recall the ui to update
            figure, ax = plt.subplots(1, 1)
            plot_window = UIPlotWindow(
                self.get_a_rect(),
                self._UI_MANAGER,
                figure,
                window_display_title=plot_name,
                object_id=f"#plot_window",
                resizable=True,
            )
            self.ui_plot_windows[plot_name] = plot_window
            # The first ax is automatically the first line
            self.axes[plot_name] = [ax]
            for plot_line in self.plots[plot_name].plot_lines[1:]:
                # If other plot lines have different y values
                if not plot_line.share_y:
                    self.axes[plot_name].append(ax.twinx())

            self.lines[plot_name] = []

            # plot_window.get_container().set_image(figure)
            # plot_window._created = False
            logger.info("Graph added.")
            logger.debug(f"Graph: {plot_window}.")
        else:
            plot_window = self.ui_plot_windows[plot_name]

        if len(self.model_outputs) < 2:
            # Cannot plot lines if only one point
            return

        # Now it is created
        plot_window._created = True
        plot_window.update_window_image()
        self.logger.debug(f"FigureSurf {plot_window.figuresurf}")

    def show_plots_list(self):
        x, y = self._menu_button_position
        width = 100
        heigth = 30
        if self._plot_list_buttons:
            for button in self._plot_list_buttons:
                button.show()
        else:
            # Create
            del self._plot_list_buttons
            self._plot_list_buttons = [
                UIButton(
                    relative_rect=pygame.Rect(
                        x, y + i * heigth, width, heigth
                    ),
                    text=name,
                    manager=self.UI_MANAGER,
                )
                for i, name in enumerate(self.plots.keys())
            ]

    # Adding plots methods

    def process_events(self, event: pygame.event.Event):
        """Process the events from the main loop."""
        self._UI_MANAGER.process_events(event)
        match event:
            case pygame.event.EventType(
                type=pygame_gui.UI_BUTTON_PRESSED, ui_object_id="#plots_button"
            ):
                self.show_plots_list()
            case pygame.event.EventType(type=pygame_gui.UI_BUTTON_PRESSED):
                if event.ui_element in self._plot_list_buttons:
                    self.logger.info(f"Create Plot {event.ui_element.text}")
                    self._create_plot_window(event.ui_element.text)
                    # Deletes all the buttons
                    for button in self._plot_list_buttons:
                        button.hide()
            case pygame.event.EventType(type=pygame_gui.UI_WINDOW_CLOSE):
                if event.ui_element in self.ui_plot_windows:
                    # Remove the window
                    window: UIPlotWindow = event.ui_element
                    del self.ui_plot_windows[window.window_display_title]

            case pygame.event.EventType(type=pysimgame.ModelStepped):
                # Update the plot on a separated thread
                if (
                    self._content_thread is None
                    or not self._content_thread.is_alive()
                ):
                    del self._content_thread
                    self._content_thread = threading.Thread(
                        target=self.update, name="Plot Update"
                    )
                    self._content_thread.start()
                    self.logger.debug(
                        f"Thread Started : {self._content_thread}"
                    )

    def update(self):
        """Update the plots based on the new outputs.

        All the windows are updated with their parameters one by one.
        """
        model_outputs = self.MODEL_MANAGER.outputs
        x = self.MODEL_MANAGER.time_axis.copy()
        if len(model_outputs) < 2:
            # Cannot plot lines if only one point
            return

        for plot_name, plot_window in self.ui_plot_windows.items():
            logger.info(f"Plotting {plot_window}.")
            if not plot_window.visible:
                # If the window is not visible
                continue

            if not plot_window._created:
                self._create_plot_window(plot_name)

            # First get the ax and cleans it
            axes = self.axes[plot_name]
            for ax in axes:
                ax.clear()
                ax.set_xlim(x[0], x[-1])

            # Will follow the ax on which to plot
            ax_index = int(0)
            # Plot all the lines required
            for plot_line in self.plots[plot_name].plot_lines:
                ax = axes[ax_index]
                ax_index += 0 if plot_line.share_y else 1

                if plot_line.y_lims is not None:
                    ax.set_ylim(plot_line.y_lims)
                # Gets the attributes
                y = (
                    (
                        self.model_outputs[
                            plot_line.region, plot_line.attribute
                        ]
                        .to_numpy()
                        .reshape(-1)
                    )
                    if isinstance(plot_line.attribute, str)
                    else np.c_[  # Concatenate the values
                        [
                            self.model_outputs[plot_line.region, attr]
                            .to_numpy()
                            .reshape(-1)
                            for attr in plot_line.attribute
                        ]
                    ].T
                )
                if "label" not in plot_line.kwargs:
                    plot_line.kwargs[
                        "label"
                    ] = plot_line.attribute or " ".join(
                        (plot_line.region, plot_line.attribute)
                    )
                artists = ax.plot(
                    x,
                    y,
                    # color=self.region_colors[plot_line.region],
                    **plot_line.kwargs,
                )
                logger.debug(
                    f"Plotting {plot_line.region} {plot_line.attribute}."
                )
                logger.debug(f"Setting: \n x: {x} \n y: {y}.")

                ax.legend()

            # lock the figsurface, so it is not used during the drawing
            self._figsurface_locks[plot_name].acquire()
            self.logger.debug(
                f"Lock acquired : {self._figsurface_locks[plot_name]}"
            )
            plot_window.figuresurf.canvas.draw()
            plot_window.update_window_image()
            self._figsurface_locks[plot_name].release()
            # plot_window.figuresurf.canvas.flush_events()
            # plot_window.get_container().set_image(plot_window.figuresurf)

    def draw(self):
        # Call the thread drawing the plot
        # if self._surface_thread is None or not self._surface_thread.is_alive():
        #     self._surface_thread = threading.Thread(
        #         target=self._draw, name="Drawing Plots on MAIN_DISPLAY"
        #     )
        #     self._surface_thread.start()
        #     self.logger.debug(f"Thread Started : {self._surface_thread}")
        self._draw()
        # Draw the UI
        self._UI_MANAGER.draw_ui(self.GAME_MANAGER.MAIN_DISPLAY)

    def _draw(self):
        # Aquire the lock on all the active plots
        locks = [
            self._figsurface_locks[name]
            for name in self.ui_plot_windows.keys()
        ]
        for lock in locks:
            lock.acquire()
            self.logger.debug(f"Lock acquired : {lock}")
        # Gets the time required for the UI MANAGER update
        _time_elapsed = time.time() - self._last_time
        self._UI_MANAGER.update(_time_elapsed)
        self._last_time = time.time()

        for lock in locks:
            lock.release()
            self.logger.debug(f"Lock released : {lock}")

    def quit(self):
        self._content_thread.join()

    def coordinates_from_serie(self, serie):
        """Convert a serie to pixel coordinates.

        Need to rescale the values of the serie to
        the ones of the display.
        Also needs to convert geometry startig from
        top to down.
        """
        pixels_x, pixels_y = self.get_size()

        # Split the x y values of the serie
        x_axis = serie.keys().to_numpy()
        y_axis = serie.values

        # Rescale to screen size between 0 and 1
        x_norm = normalize(x_axis)
        y_norm = normalize(y_axis)
        # y starts from the bottom instead of top
        y_norm = 1.0 - y_norm

        # Compute the positions on the screen
        x_screen = pixels_x * x_norm
        y_screen = pixels_y * y_norm

        # Return as list of pygame coordinates
        return [(x, y) for x, y in zip(x_screen, y_screen)]
