"""Graphs models for ills fate."""

import os
from typing import Tuple
from .utils.maths import normalize
import pygame

from pygame import draw

import matplotlib
matplotlib.use('module://pygame_matplotlib.backend_pygame')

import matplotlib.pyplot as plt

COLORS_LIST = (
    'red', 'blue', 'green', 'orange'
)

REGION_COLORS = {
    ''
}


class GraphsSurface(pygame.Surface):
    """A surface for the graphs that handles which graphs are shown."""

    outgraph_ratio: float = 0.1  # Part of the surface for labels and axes
    axis_zero_zero_position: Tuple[int, int]

    def __init__(self, *args, region_colors_dict,  **kwargs) -> None:
        """Initialize the graphs surface.

        Same args as pygame.Surface().
        """
        super().__init__(*args, **kwargs)

        self.previous_serie = None
        print(region_colors_dict)
        self.region_colors = region_colors_dict
        size = self.get_size()
        self.axis_zero_zero_position = (
            int(size[0] * self.outgraph_ratio),
            int(size[1] * (1 - self.outgraph_ratio))
        )

        self.figure, self.ax = plt.subplots()

    def parse_initial_serie(self, serie):
        self.previous_serie = serie
        # Attributes a color to each region
        self.colors = {
            region: COLORS_LIST[i]
            for i, region
            in enumerate(serie.index.levels[0])  # Access the region names
        }

    def update_graphs(self, current_serie):
        """Add the current serie to the graphs.

        Not Implemented.
        """
        if self.previous_serie is None:
            self.parse_initial_serie(current_serie)
            return

        time = self.time()
        for (region, variable), value in current_serie.items():

            draw.line(
                self,
                self.colors[region],
            )

    def plot(self, outputs):
        """Plot the outputs of the model."""
        if len(outputs) < 2:
            # Cannot plot lines if only one point
            return
        self.fill('black')
        self.ax.clear()
        self.figure.fill('white')
        # Plot the regions graphs
        for (region, variable), serie in outputs.items():
            self.ax.plot(serie, color=self.region_colors[region]/255)
        # Plots the axis
        draw.circle(
            self, color='red',
            center=self.axis_zero_zero_position, radius=20
        )
        self.figure.canvas.draw()
        self.blit(self.figure, (0, 0))

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
        y_norm = 1. - y_norm

        # Compute the positions on the screen
        x_screen = pixels_x * x_norm
        y_screen = pixels_y * y_norm

        # Return as list of pygame coordinates
        return [(x, y) for x, y in zip(x_screen, y_screen)]
