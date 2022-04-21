"""Provide an Abstract manager for plots."""
from __future__ import annotations

from abc import abstractmethod
from importlib.machinery import SourceFileLoader
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import pygame
import pygame_gui
from pysimgame.model import ModelManager
from pysimgame.plotting.plot import Plot
from pysimgame.utils.abstract_managers import GameComponentManager

if TYPE_CHECKING:
    from ..game_manager import GameManager

_PLOT_MANAGER: AbstractPlotsManager


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

    plots: list[Plot]

    def __init__(self, GAME_MANAGER: GameManager) -> None:
        super().__init__(GAME_MANAGER)
        self.plots = []
        # Register the plot manager being this
        global _PLOT_MANAGER
        _PLOT_MANAGER = self

    def connect(self):
        self._connect_to_model(self.GAME_MANAGER.MODEL_MANAGER)

    def _connect_to_model(self, MODEL_MANAGER: ModelManager):
        """Connect the plots display to the models."""
        self.model_outputs = MODEL_MANAGER.outputs
        self.MODEL_MANAGER = MODEL_MANAGER

        # Create a df containing regions and alements
        self.df_keys = self.model_outputs.keys().to_frame(index=False)

        # Load the plots
        plots_dir = Path(self.GAME.GAME_DIR, "plots")
        if not plots_dir.exists():
            plots_dir.mkdir()
        plots_files = list(plots_dir.rglob("*.py"))
        # Read what is in the files
        for file in plots_files:
            SourceFileLoader("", str(file)).load_module()

        self.logger.debug(f"Files: {plots_files}")
        # Register connected
        self._connected = True

    def register_plot(self, plot: Plot):
        """Add a :py:class:`Plot` to the manager.

        The :py:class`Plot`s can be then accessed
        using `self.plots[name]` .
        """
        self.logger.debug(f"Adding {plot = }")

        self.plots.append(plot)

    @abstractmethod
    def show_plots_list(self):
        """Show all the available plots on the GUI.

        This is triggered when the user presses the plot menu.
        """
        ...

    def process_events(self, event: pygame.event.Event) -> bool:
        """Listen to the events that require drawing a plot."""
        match event:
            case pygame.event.EventType(
                type=pygame_gui.UI_BUTTON_PRESSED, ui_object_id="#plots_button"
            ):
                # The button menu that opens the plot list
                self.show_plots_list()
                return True

        return False

    @abstractmethod
    def draw(self):
        """Draw the plot.

        This will be called on a separate thread,
        so make sure that when you write a variable
        you don't create race conditions.
        """

        ...
