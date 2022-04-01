from pathlib import Path

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import pygame

from pysimgame.events import ModelStepped
from .types import TestVariables, TrainVariables
from pysimgame.utils import GameComponentManager

if TYPE_CHECKING:
    from pysimgame.model import AbstractModelManager


class MLVarMngr(GameComponentManager):
    """Manager for ML variables.

    Listen the Model manager and store the current variables
    into a file for later used by an optimisation algorithm.

    The arrays stored contain :math:`n_{x_var}` the number of variables
    that should be optimized from :math:`\\mathcal{x}`,
    :math:`n_{samples}` the number of steps that the model registered
    and store,
    :math:`n_{y_var}` the number of variables that are
    predicted/targeted, i.e. the size of the output values that are
    compared to the real data,
    :math:`n_{records}`, the number of records of real data existing
        if you are having a simple setup, this might be 1.

    :param x_train: An array of size :math:`(n_{sample},n_{x_var})`
        for the training data.
    :param y_pred: An array of size :math:`(n_{sample},n_{y_var})`
        for the output from the model using the matchin x_train vars.
    :param y_target: An array of size :math:`(n_{records},n_{y_var})`
        the real values for the variables.
    """

    MODEL_MANAGER: AbstractModelManager

    x_variables: TrainVariables
    y_variables: TestVariables
    x_train: np.ndarray
    y_pred: np.ndarray
    y_target: np.ndarray

    metadata: pd.DataFrame

    def prepare(self):

        # Create the directories desired
        self.DIR = Path(self.GAME.GAME_DIR, "ml")
        self.DIR.mkdir(exist_ok=True)
        self.DATA_DIR = Path(self.DIR, "data")
        self.DATA_DIR.mkdir(exist_ok=True)

        self.MODEL_MANAGER = self.GAME_MANAGER.MODEL_MANAGER

        self.metadata = pd.DataFrame(columns=["time", "region"])

    def connect(self):
        """Read the variables of the model manager."""

        # Visit the model to get the variables
        (
            self.x_variables,
            self.y_variables,
        ) = self.MODEL_MANAGER.accept_ml_vars_mngr(self)
        # Create empty arrays for storing variables
        self.x_train = np.empty((0, len(self.x_variables)))
        self.y_pred = np.empty((0, len(self.y_variables)))

    def process_events(self, event: pygame.event.Event) -> bool:
        """Listen the events for this manager."""
        match event:
            case pygame.event.EventType(type=ModelStepped):
                self.read_model()
                return False

    def read_model(self):
        """Read the current variables in the model."""
        self.MODEL_MANAGER.model_lock.acquire()

        for region, model in self.MODEL_MANAGER.models.items():
            # Add the current settings to the ml data
            new_x = np.array(
                # Note: i removed a () which was in pysd
                # maybe that is a bug
                [getattr(model, attr) for attr in self.x_variables]
            ).reshape((1, -1))

            self.x_train = np.concatenate((self.x_train, new_x))
            new_y = np.array(
                # Note: i removed a () which was in pysd
                # maybe that is a bug
                [getattr(model, attr) for attr in self.y_variables]
            ).reshape((1, -1))
            self.y_pred = np.concatenate((self.y_pred, new_y))
            # Add the meta data
            self.metadata.append(
                {"time": getattr(model, "time"), "region": region}
            )

        self.MODEL_MANAGER.model_lock.release()
