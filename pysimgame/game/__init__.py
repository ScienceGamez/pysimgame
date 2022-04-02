"""Helper for Game definition from pysimgame."""
from __future__ import annotations
from functools import cached_property

import json
import logging
from pathlib import Path
import shutil
from typing import TYPE_CHECKING, Any
from pysimgame.regions_display import RegionComponent, SingleRegionComponent

from pysimgame.utils.directories import (
    FORBIDDEN_GAME_NAMES,
    GAME_SETTINGS_FILENAME,
    INITIAL_CONDITIONS_FILENAME,
    MODEL_FILENAME,
    PYSDGAME_DIR,
    REGIONS_FILE_NAME,
)

if TYPE_CHECKING:
    from pysimgame.types import RegionsDict, ModelType


def list_available_games() -> list[Game]:
    """Return the game availables."""
    subdirs = PYSDGAME_DIR.glob("*/")
    return [
        Game(game_dir.stem)
        for game_dir in subdirs
        if game_dir.is_dir() and game_dir.stem not in FORBIDDEN_GAME_NAMES
    ]


class GameNotFoundError(Exception):
    """A game was not found."""

    game: str
    game_dir: Path
    msg: str

    def __init__(self, game: str, game_dir: Path) -> None:
        self.msg = f"Game '{game}' cannot be found in {game_dir}"
        super().__init__(self.msg)


class Game:
    """Helper class representing a game type from pysd.

    Holds meta information on a game.
    Games all have a model they are based on and a set of settings to
    define how they should be played.

    :arg name: The name of the game
    :arg create: Whether the game should be created
    :arg game_dir: The directory where the game should be created.
        If not specified, pysimgame will choose a default.
    """

    NAME: str
    GAME_DIR: Path
    REGIONS_FILE: Path
    INITIAL_CONDITIONS_FILE: Path
    PYSD_MODEL_FILE: Path
    SETTINGS: dict[str, Any]

    REGIONS_DICT: RegionsDict

    _allow_delete: bool

    def __new__(cls, name: str | Game, *args, **kwargs):
        if isinstance(name, cls):
            # Return the game if a game object was given
            return name
        else:
            return object.__new__(cls)

    def __init__(
        self,
        name: str | Game,
        create: bool = False,
        game_dir: Path = None,
    ) -> None:
        self.logger = logging.getLogger(f"Game.{name}")
        self._allow_delete = False
        self.NAME = name
        self.GAME_DIR = game_dir or Path(PYSDGAME_DIR, name)
        # Ensure the path is as Path and not str if given by user
        self.GAME_DIR = Path(self.GAME_DIR)
        match self.GAME_DIR.exists(), create:
            case False, True:  # Game creation
                self.GAME_DIR.mkdir()
            case False, False:  # Reading a non existing game
                raise GameNotFoundError(self.NAME, self.GAME_DIR)
        self.REGIONS_FILE = Path(self.GAME_DIR, REGIONS_FILE_NAME)
        self.PYSD_MODEL_FILE = Path(self.GAME_DIR, MODEL_FILENAME)
        self.INITIAL_CONDITIONS_FILE = Path(
            self.GAME_DIR, INITIAL_CONDITIONS_FILENAME
        )
        self._SETTINGS_FILE = Path(self.GAME_DIR, GAME_SETTINGS_FILENAME)

    @cached_property
    def SINGLE_REGION(self) -> bool:
        """Whether the game has only one region."""
        return len(self.REGIONS_DICT) <= 1

    @cached_property
    def REGIONS_DICT(self) -> RegionsDict:
        """Load the dictionary of the regions for that game."""
        with open(self.REGIONS_FILE, "r") as f:
            dic = json.load(f)
        self.logger.info("Region file loaded.")
        self.logger.debug(f"Region file content: {dic}.")

        return (
            {  # Load regions from what is in the file
                region_dict["name"]: RegionComponent.from_dict(region_dict)
                for region_dict in dic.values()
            }
            if len(dic) != 0
            # Load a single region if they are not in the file
            else {"": SingleRegionComponent()}
        )

    @cached_property
    def SETTINGS(self) -> dict[str, Any]:
        """Load the settings of the game."""

        with open(self._SETTINGS_FILE, "r") as f:
            settings = json.load(f)
        # Check everything necessary is in settings, else add
        if "Themes" not in settings:
            settings["Themes"] = {}
        self.logger.info("Game Settings loaded.")
        self.logger.debug(f"Game Settings content: {settings}.")
        return settings

    def save_settings(self) -> None:
        """Save the game settings.

        Settings can be modified directly by calling Game.SETTINGS .
        The settings will only be saved using this method.
        """

        with open(self._SETTINGS_FILE, "w") as f:
            json.dump(f, self.SETTINGS)
        self.logger.info("Game Settings saved.")
        self.logger.debug(f"Game Settings content: {self.SETTINGS}.")

    def load_model(self) -> ModelType:
        """Return a model object for doc purposes.

        ..note:: currently works only with pysd models.
        """
        import pysd

        model = pysd.load(self.PYSD_MODEL_FILE)
        return model.components

    def delete(self):
        """Delete the game.

        Remove all game files.
        For security, you need to set manually the variable
        self._allow_delete to True.
        """
        if self._allow_delete == True:
            self.logger.warn(f"Deleting {self}")
            shutil.rmtree(self.GAME_DIR)
        else:
            self.logger.warn(
                f"Did not delete {self}, as 'self._allow_delete != True' "
            )

    def __str__(self) -> str:
        return f"Game {self.NAME}"
