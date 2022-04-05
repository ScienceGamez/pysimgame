"""Helper for Game definition from pysimgame."""
from __future__ import annotations
from functools import cached_property
from numpy import True_

from packaging.version import Version
import git

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
    REPOSITORY_URL,
)

if TYPE_CHECKING:
    from pysimgame.types import RegionsDict, ModelType


def guess_game_name_from_clone_arg(arg: str) -> str:
    """Guess the name of the game from the --clone argument."""
    if "/" in arg:
        # If url, probably the last value is used as game name
        return arg.split("/")[-1]
    else:
        arg


def list_available_games(games_dir: Path = PYSDGAME_DIR) -> list[Game]:
    """Return the game availables in the specified directory.

    :arg games_dir: The directory in which the games are to be searched.
    """
    subdirs = games_dir.glob("*/")
    return [
        Game(game_dir.stem, game_dir=games_dir)
        for game_dir in subdirs
        if game_dir.is_dir() and game_dir.stem not in FORBIDDEN_GAME_NAMES
    ]


class GameNotFoundError(Exception):
    """A game was not found."""

    game_dir: Path
    msg: str

    def __init__(self, game_dir: Path) -> None:
        self.msg = f"Game '{game_dir.stem}' cannot be found as path {game_dir}"
        super().__init__(self.msg)


class GameAlreadyExistError(Exception):
    """A game already exists."""

    game_dir: Path
    msg: str

    def __init__(self, game_dir: Path) -> None:
        self.msg = f"Game '{game_dir.stem}' already exists at path {game_dir}"
        super().__init__(self.msg)


class Game:
    """Helper class representing a game type from pysd.

    Holds meta information on a game.
    Games all have a model they are based on and a set of settings to
    define how they should be played.

    A game will be found at `game.GAME_DIR = Path(game_dir, name)`

    :arg name: The name of the game
    :arg create: Whether the game should be created
    :arg game_dir: The directory where the game should be created.
        If not specified, pysimgame will choose a default.
    :arg remote: If combined with create=True, this will create
        the game from an online repository.
    """

    NAME: str
    GAME_DIR: Path
    VERSION: str
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
        remote: str = "",
    ) -> None:

        self.logger = logging.getLogger(f"Game.{name}")
        self._allow_delete = False
        self.NAME = name
        if game_dir is None:
            # Default path
            self.GAME_DIR = Path(PYSDGAME_DIR, name)
        else:
            # Ensure the path is as Path and not str if given by user
            self.GAME_DIR = Path(game_dir, name)
        match self.GAME_DIR.exists(), create, remote:
            case True, True, rem:  # Game already exists
                raise GameAlreadyExistError(self.GAME_DIR)
            case False, True, "":  # Game creation local
                self.logger.info(f"Creating local game at {self.GAME_DIR}")
                self.GAME_DIR.mkdir()
            case False, True, rem:  # Game creation from repo
                self.logger.info(
                    f"Creating game at {self.GAME_DIR} from {remote}"
                )
                self.GAME_DIR.mkdir()
                self.download_game(remote)
            case False, False, "":  # Reading a non existing game
                raise GameNotFoundError(self.GAME_DIR)
            case True, False, "":  # The game is read
                self.logger.info(f"Reading game at {self.GAME_DIR}")
            case _:
                print(f"{self.GAME_DIR.exists()=}, {create=}, {remote=}")
                raise ValueError("Unexpected arguments combination.")

        # Set some file paths
        self.REGIONS_FILE = Path(self.GAME_DIR, REGIONS_FILE_NAME)
        self.PYSD_MODEL_FILE = Path(self.GAME_DIR, MODEL_FILENAME)
        self.INITIAL_CONDITIONS_FILE = Path(
            self.GAME_DIR, INITIAL_CONDITIONS_FILENAME
        )
        self._SETTINGS_FILE = Path(self.GAME_DIR, GAME_SETTINGS_FILENAME)

    def add_readme(self, exist_ok: bool = False):
        """Add a default readme to the game dir.

        :arg exist_ok: If the readme already exists,
            the function succeeds if *exist_ok*
            is true ,
            otherwise :exc:`FileExistsError` is raised.
        """
        readme = "\n".join(
            (
                f"# {self.NAME}",
                "",
                "To install, you need to follow the instructions from"
                " [pysimgame]"
                "(https://pysimgame.readthedocs.io/en/latest/installation/index.html#requirements)",
                "",
                "Then you can run",
                "```",
                f"python -m pysimgame {self.NAME} --clone",
                "```",
                f"This will install {self.NAME} game locally.",
                "",
                f"This game was created using "
                f"[pysimgame]({REPOSITORY_URL + 'pysimgame'}).",
            )
        )
        readme_file = Path(self.GAME_DIR, "README.md")
        if readme_file.exists():
            if exist_ok:
                return
            else:
                raise FileExistsError(readme_file)

        with open(readme_file, "w") as f:
            f.write(readme)

    def download_game(self, remote_url: str):
        """Download the game."""
        if "/" not in remote_url:
            remote_url = REPOSITORY_URL + remote_url
        # Download from the remote git repo
        git.Repo.clone_from(remote_url, self.GAME_DIR)
        git.Repo(self.GAME_DIR)

    def publish_game(self, remote_url: str):
        """Upload the game to a remote repository."""
        try:
            repo = git.Repo(self.GAME_DIR)
        except:
            repo = git.Repo.init(self.GAME_DIR)
        try:
            remote = repo.remote("pysimgame")
            remote.set_url(remote_url)
        except ValueError as ve:
            # The remote does not exist in folder yet
            remote = repo.create_remote("pysimgame", url=remote_url)
        self.logger.debug(f"{remote=} {remote.exists()}")

        remote.fetch()

        # repo.git.checkout("-b", "pysimgame")
        self.add_readme(exist_ok=True)
        repo.git.add(".")
        repo.git.commit("-m", "[by pysimgame] Publishing game")
        repo.git.branch("-M", "master")

        repo.git.push(*["--set-upstream", "pysimgame", "master"])
        # try:
        #     repo.git.push(["--set-upstream", "pysimgame", "master"])
        # except git.GitCommandError as gce:
        #     print("Error in git push command:", gce.stderr)

    def push_game(self):
        """Push the updates to the remote."""
        repo = git.Repo(self.GAME_DIR)
        # repo.git.checkout("-b", "pysimgame")
        self.add_readme(exist_ok=True)
        repo.git.add(".")
        repo.git.commit("-m", "[by pysimgame] Updated game")
        repo.remote("pysimgame").push()

    @property
    def VERSION(self) -> Version:
        version_file = Path(self.GAME_DIR, ".version")
        if version_file.exists():
            version = Version(version_file.read_text())
        else:
            version = Version("0.0.0")
            self.logger.info(f"No version found, using default {version}")
            with open(version_file, "w") as f:
                f.write(str(version))
        return version

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
