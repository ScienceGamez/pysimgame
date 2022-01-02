from __future__ import annotations

from importlib.machinery import SourceFileLoader
from pathlib import Path
from typing import TYPE_CHECKING

from pysimgame.utils import GameComponentManager

if TYPE_CHECKING:
    from pysimgame.model import ModelManager

_LINKS_MANAGER: LinksManager


class BaseLink:
    """Base class for all the linking classes."""

    LINKS_MANAGER: LinksManager

    def __init__(self) -> None:
        self.LINKS_MANAGER = _LINKS_MANAGER


class LinksManager(GameComponentManager):
    """Manager for the links between regions and model variables.

    Links are applied to the model during connect()
    """

    MODEL_MANAGER: ModelManager
    LINKS_DIR: Path

    def prepare(self):
        self.LINKS_DIR = Path(self.GAME.GAME_DIR, "links")
        global _LINKS_MANAGER
        _LINKS_MANAGER = self
        from .shared_variables import SharedVariables

        self.shared_variables = SharedVariables()

    def connect(self):
        self.MODEL_MANAGER = self.GAME_MANAGER.MODEL_MANAGER
        # Finds all files
        links_files = list(self.LINKS_DIR.rglob("*.py"))
        self.logger.debug(f"Files: {links_files}")
        # TODO: see if we want to add security in the files loaded
        for file in links_files:
            # Create a special name to not override attributes
            module_name = f"_{file.stem}"
            # Importing the files will execute the code that changes
            # the model manager.
            SourceFileLoader(module_name, str(file)).load_module()

        # Process the link into the model
        self.MODEL_MANAGER.link_shared_variables(self.shared_variables)
