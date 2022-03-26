"""Provide an Abstract manager for plots."""
from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

import pygame
from pysimgame.plotting.plot import Plot
from pysimgame.utils import GameComponentManager

if TYPE_CHECKING:
    from ..game_manager import GameManager


class AbstractPlotsManager(GameComponentManager):
    """The abstract plot manager.

    Provide a minimal required implememntation for a plot manager.

    The goal is that you can use any programm you want to see
    the plots, once you provide an implmementation of this.

    As the drawing process can be an expansive process,
    this managers handles the creation of a special thread
    calling :py:meth:`AbstractPlotsManager.draw` .

    TODO: finalize implementation
    1. Make the thread for the draw function.
    """

    pass

    @abstractmethod
    def add_plot(self, name: str, plot: Plot):
        """Add a :py:class:`Plot` to the manager."""
        ...

    @abstractmethod
    def show_plots_list(self):
        """Show all the available plots."""
        ...

    def process_events(self, event: pygame.event.Event) -> bool:
        """Listen to the events that require drawing a plot."""
        ...
        # TODO implement the events

    @abstractmethod
    def draw(self):
        """Draw the plot.

        This will be called on a separate thread,
        so make sure that when you write a variable
        you don't create race conditions.
        """

        ...
