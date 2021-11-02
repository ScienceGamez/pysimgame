"""Graphs models for ills fate.

The Graph manager handles graphs creations and transfer of data from
the model.
Different graphs window can be created:
    - Parameters evolution graph. Can plot the parameters of a model
        though time.
    - Regions evolution graph. Plot the same parameter across regions.
    - Regions comparison heatmap.
"""

import os
from typing import List, Tuple, Type
from matplotlib import interactive
import numpy as np

import pandas
from pandas.core import series

from pysdgame.model import ModelManager
from pysdgame.utils.strings import beautify_parameter_name
from .utils.maths import normalize
import pygame

from pygame import draw

from pygame_matplotlib.gui_window import UIPlotWindow


import matplotlib.pyplot as plt

COLORS_LIST = ("red", "blue", "green", "orange")

REGION_COLORS = {""}

Region: Type[str] = str


class GraphsManager:
    """A manager for graphs.

    Register all the graphs that were created and that are now active.
    Updates the at every step with the new data.
    """

    ui_plot_windows: List[UIPlotWindow] = []
    model_outputs: pandas.DataFrame
    _connected: bool = False

    def __init__(self, region_colors_dict, ui_manager) -> None:
        """Initialize the graphs surface.

        Same args as pygame.Surface().
        """

        self.previous_serie = None
        print(region_colors_dict)
        self.region_colors = region_colors_dict
        self.ui_manager = ui_manager

    def parse_initial_outputs(self, model_outputs):

        # Create a df containing regions and alements
        keys_df = model_outputs.keys().to_frame(index=False)
        keys_df["regions"].unique()
        keys_df["elements"].unique()

        for plot_window in self.ui_plot_windows:
            pass

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
        self.ui_plot_windows.append(
            plot_window := UIPlotWindow(
                self.get_a_rect(), self.ui_manager, figure, resizable=True
            )
        )
        plot_window.regions = regions
        plot_window.elements = elements
        plot_window.ax = ax
        plot_window.figure = figure
        plot_window.artists = []
        plot_window.get_container().set_image(figure)
        plot_window._created = False

        if self._connected:
            self._create_plot_window(plot_window)

    def _create_plot_window(self, plot_window: UIPlotWindow):
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
                    color=self.region_colors[region] / 255,
                    animated=True,
                )
                for a in artists:
                    a.region = region
                    a.element = element
                plot_window.artists.extend(artists)

        # Set a title to the window
        self.set_window_title(plot_window)

        self.full_redraw(plot_window)

        # Now it is created
        plot_window._created = True

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

    def update(self, model_outputs: pandas.DataFrame):
        """Update the graphs based on the new outputs.

        All the windows are updated with their parameters one by one.
        """
        if len(model_outputs) < 2:
            # Cannot plot lines if only one point
            return

        for plot_window in self.ui_plot_windows:

            if not plot_window.visible:
                # If the window is not visible
                continue

            if not plot_window._created:
                self._create_plot_window(plot_window)

            # plot_window.ax.clear()

            for artist in plot_window.artists:
                # Creates the array of y data with nan values
                y = np.full_like(self.time_axis, np.nan)
                serie = self.model_outputs[artist.region, artist.element]
                y[: len(serie)] = serie.to_numpy().reshape(-1)
                # Update the artist data
                artist.set_ydata(y)
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

    def connect_to_model(self, model_manager: ModelManager):
        """Connect the graphs display to the models."""
        self.model_outputs = model_manager.outputs

        # Create a df containing regions and alements
        self.df_keys = self.model_outputs.keys().to_frame(index=False)

        # Time axis
        self.time_axis = model_manager.time_axis

        # Check existing graphs
        for plot_window in self.ui_plot_windows:
            if plot_window.regions is None:
                plot_window.regions = self.df_keys["regions"].unique()
            if plot_window.elements is None:
                plot_window.elements = self.df_keys["elements"].unique()

        # Register connected
        self._connected = True
