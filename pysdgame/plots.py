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
from typing import TYPE_CHECKING, Dict, List, Tuple, Type
from matplotlib.lines import Line2D
import numpy as np


import pandas
from pygame_gui import elements
import pygame_gui
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.ui_manager import UIManager
from pygame_matplotlib.backend_pygame import FigureSurface
from pygame_matplotlib import pygame_color_to_plt
from pysdgame.game_manager import GameComponentManager


from pysdgame.model import ModelManager
from pysdgame.utils.logging import logger
from pysdgame.utils.strings import beautify_parameter_name
from .utils.maths import normalize
import pygame


from pygame_matplotlib.gui_window import UIPlotWindow

if TYPE_CHECKING:
    from pysdgame.game_manager import GameManager
    from .game_manager import GameManager
    import matplotlib
    import matplotlib.axes
    import matplotlib.artist

import matplotlib.pyplot as plt

COLORS_LIST = ("red", "blue", "green", "orange")

REGION_COLORS = {""}

Region: Type[str] = str


class PysgamePlotWindow(UIPlotWindow):
    """Attributes for a pysdgame plot."""

    # Stores the info on what to plot
    regions: List[str]
    elements: List[str]
    _regions: List[str]
    _elements: List[str]
    # Stores the elements of the figure
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
    def elements(self) -> List[str]:
        return self._elements

    @elements.setter
    def elements(self, elements: List[str]):
        if elements is None:
            elements = []
        self._elements = list(elements).copy()

    def __str__(self) -> str:
        return "Plot window: \n \t Regions {} \t Elements: {}".format(
            self.regions, self.elements
        )


class PlotsManager(GameComponentManager):
    """A manager for plots.

    Register all the plots that were created and that are now active.
    Updates the at every step with the new data.
    """

    ui_plot_windows: List[PysgamePlotWindow]
    GAME_MANAGER: GameManager
    MODEL_MANAGER: ModelManager
    _connected: bool = False
    region_colors: Dict[str, Tuple[float, float, float, float]]

    # Initialization Methods #

    def prepare(self):
        """Prepare the graph manager."""
        self.ui_plot_windows = []
        self.previous_serie = None

        self._read_regions_colors()
        # TODO: think if we want a separated UI Manager for plots
        self.ui_manager = self.GAME_MANAGER.UI_MANAGER

    def _read_regions_colors(self):
        self.region_colors = {
            name: pygame_color_to_plt(cmpnt.color)
            for name, cmpnt in self.GAME_MANAGER.game.REGIONS_DICT.items()
            if name is not None
        }
        logger.debug(f"Regions Color {self.region_colors}")

    def connect(self):
        self._connect_to_model(self.GAME_MANAGER.MODEL_MANAGER)

    def _connect_to_model(self, MODEL_MANAGER: ModelManager):
        """Connect the plots display to the models."""
        self.model_outputs = MODEL_MANAGER.outputs
        self.MODEL_MANAGER = MODEL_MANAGER

        # Create a df containing regions and alements
        self.df_keys = self.model_outputs.keys().to_frame(index=False)

        # Time axis
        self.time_axis = MODEL_MANAGER.time_axis

        # Check existing plots
        for plot_window in self.ui_plot_windows:
            if plot_window.regions is None:
                plot_window.regions = self.df_keys["regions"].unique()
            if plot_window.elements is None:
                plot_window.elements = self.df_keys["elements"].unique()

        # Register connected
        self._connected = True

    # Adding plots methods

    def get_a_rect(self) -> pygame.Rect:
        """Return a rect from a nice place in the main window.

        TODO: make it a nice place for real...
        """
        return pygame.Rect(0, 0, 300, 300)

    def add_graph(
        self,
        elements: List[str] = None,
        regions: Tuple[List[Region], Region] = None,
    ) -> None:
        """Add a graph to the game.

        Args:
            elements: The name of the variables to be plotted. If None,
                will look at all the available elements.
            regions: The regions which should be on the plot. If None,
                plot all the regions.
        """
        # Needs to recall the ui to update
        figure, ax = plt.subplots(1, 1)
        plot_window = PysgamePlotWindow(
            self.get_a_rect(), self.ui_manager, figure, resizable=True
        )
        self.ui_plot_windows.append(plot_window)

        # Attributes all elements or all regions in case not defined
        if regions is None:
            regions = self.GAME.REGIONS_DICT.keys()
        plot_window.regions = regions
        if elements is None:
            elements = self.MODEL_MANAGER.elements_names
        plot_window.elements = elements
        plot_window.ax = ax
        plot_window.figure = figure
        plot_window.artists = []
        plot_window.get_container().set_image(figure)
        plot_window._created = False
        logger.info("Graph added.")
        logger.debug(f"Graph: {plot_window}.")
        if self._connected:
            self._create_plot_window(plot_window)

    def _create_plot_window(self, plot_window: PysgamePlotWindow):
        """Create the plot on the window.

        Assume plot_window has regions and elements it need to plot.
        """
        if len(self.model_outputs) < 2:
            # Cannot plot lines if only one point
            return

        # Plot all the lines required
        for region in plot_window.regions:
            for element in plot_window.elements:
                if element == "time":
                    continue
                y = np.full_like(self.time_axis, np.nan)
                serie = self.model_outputs[region, element]
                y[: len(serie)] = serie.to_numpy().reshape(-1)
                plot_window.ax.set_xlim(self.time_axis[0], self.time_axis[-1])
                artists = plot_window.ax.plot(
                    self.time_axis,
                    y,
                    color=self.region_colors[region],
                    animated=True,
                )
                for a in artists:
                    # Remember for each artist what it represent
                    a.region = region
                    a.element = element
                plot_window.artists.extend(artists)

        # Set a title to the window
        self.set_window_title(plot_window)

        self.full_redraw(plot_window)

        # Now it is created
        plot_window._created = True

    # Adding plots methods

    def full_redraw(self, plot_window: UIPlotWindow):
        # figure, ax = plt.subplots(1, 1)

        plot_window.figuresurf.draw(plot_window.figuresurf.canvas.renderer)

    def set_window_title(self, plot_window: UIPlotWindow):
        """Find out which title should be given to the window and give it."""
        if len(plot_window.elements) == 1:
            title = plot_window.elements[0]
        elif len(plot_window.regions) == 1:
            title = plot_window.regions[0]
        else:
            title = "Custom selection"

        plot_window.set_display_title(beautify_parameter_name(title))

    def process_events(self, event: pygame.event.Event):
        """Process the events from the main loop."""
        if (
            event.type == pygame.USEREVENT
            and event.user_type == pygame_gui.UI_WINDOW_CLOSE
            and event.ui_element in self.ui_plot_windows
        ):
            # Close the winow event
            self.ui_plot_windows.remove(event.ui_element)

    def update(self):
        """Update the plots based on the new outputs.

        All the windows are updated with their parameters one by one.
        """
        model_outputs = self.MODEL_MANAGER.outputs
        x = self.MODEL_MANAGER.time_axis
        if len(model_outputs) < 2:
            # Cannot plot lines if only one point
            return

        for plot_window in self.ui_plot_windows:
            logger.info(f"Plotting {plot_window}.")
            if not plot_window.visible:
                # If the window is not visible
                continue

            if not plot_window._created:
                self._create_plot_window(plot_window)

            # plot_window.ax.clear()

            for artist in plot_window.artists:
                # Creates the array of y data with nan values
                serie = model_outputs[artist.region, artist.element]
                y = serie.to_numpy().reshape(-1)
                # Update the artist data
                artist.set_ydata(y)
                artist.set_xdata(x)
                logger.debug(f"Plotting {artist.region} {artist.element}.")
                logger.debug(f"Setting: \n x: {x} \n y: {y}.")
                plot_window.ax.draw_artist(artist)

                y_lims = plot_window.ax.get_ylim()
                if min(y) < y_lims[0] or max(y) > y_lims[1]:
                    MARGIN = 0.02
                    plot_window.ax.update_datalim(
                        [
                            (self.time_axis[0], (1 - MARGIN) * min(y)),
                            (self.time_axis[-1], (1 + MARGIN) * max(y)),
                        ]
                    )
                    self.full_redraw(plot_window)

            plot_window.figuresurf.canvas.blit()
            # plot_window.figuresurf.canvas.flush_events()
            plot_window.get_container().set_image(plot_window.figuresurf)

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
