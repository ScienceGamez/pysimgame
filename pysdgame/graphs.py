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

import pandas
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
        series: List[str] = None,
        regions: Tuple[List[Region], Region] = None,
    ) -> None:
        """Add a graph to the game.

        Args:
            series: The name of the variables to be plotted. If None,
                will look at all the available series.
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
        plot_window.series = series
        plot_window.ax = ax
        plot_window.get_container().set_image(figure)

    def update(self, model_outputs: pandas.DataFrame):
        """Update the graphs based on the new outputs.

        All the windows are updated with their parameters one by one.
        """
        if len(model_outputs) < 2:
            # Cannot plot lines if only one point
            return

        for plot_window in self.ui_plot_windows:

            if not plot_window.visible:
                continue

            plot_window.ax.clear()

            # Create a df containing regions and alements
            df = model_outputs.keys().to_frame(index=False)

            for region in plot_window.regions or df["regions"].unique():
                for variable in plot_window.series or df["elements"].unique():
                    plot_window.ax.plot(
                        model_outputs[region, variable],
                        color=self.region_colors[region] / 255,
                    )
            plot_window.figuresurf.canvas.draw()
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
