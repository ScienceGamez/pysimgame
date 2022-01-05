"""Module for creating new games."""
from __future__ import annotations

import json
import logging
import pathlib
import shutil
from typing import TYPE_CHECKING, Any, List

import pysd
from pygame import image

import pysimgame
from pysimgame.game_manager import Game

from .utils.directories import (
    BACKGROUND_DIR_NAME,
    GAME_SETTINGS_FILENAME,
    MODEL_FILESTEM,
    ORIGINAL_BACKGROUND_FILESTEM,
    PYSDGAME_DIR,
    REGIONS_FILE_NAME,
)
from .utils.logging import logger
from .utils.pysimgame_settings import PYSDGAME_SETTINGS

if TYPE_CHECKING:
    from .types import RegionsDict


def error_popup(msg: str):
    return


def get_available_games() -> List[str]:
    """Return a list of the games available for the user."""
    dir = pathlib.Path(PYSDGAME_DIR)
    existing_games = [d.name for d in dir.iterdir()]
    logger.debug("Found games : {}".format(existing_games))
    return existing_games


def check_game_name(name: str) -> None:
    # Check that it already exist

    if name == "":
        raise ValueError("Game name cannot be empty.")
    existing_games = get_available_games()

    if name in existing_games:
        raise ValueError("Name '{}' is already taken.".format(name))


def from_local_file(
    name: str,
    model_file: pathlib.Path,
    theme_file: pathlib.Path = None,
) -> None:
    return


def update_model_file(game: Game | str):
    game = Game(game)
    model_file = game.PYSD_MODEL_FILE.with_suffix(".mdl")
    parse_model_file(model_file, game.GAME_DIR)


def parse_model_file(model_filepath: pathlib.Path, game_path: pathlib.Path):
    """Read the model file and parse it into python script using pysd."""
    # Where pysimgame will store the model
    pysimgame_model_filepath = pathlib.Path(
        game_path, MODEL_FILESTEM + model_filepath.suffix
    )

    if pysimgame_model_filepath == model_filepath:
        # File is already at good location
        # We just need to parse it again
        pass
    else:
        if pysimgame_model_filepath.exists():
            logger.warn(
                f"File {pysimgame_model_filepath} already exists. "
                f"Overriden by {model_filepath}."
            )
        shutil.copyfile(  # Copy to the new location
            model_filepath, pysimgame_model_filepath
        )

    # Check which model type it is to parse it
    if pysimgame_model_filepath.suffix == ".mdl":
        # Vensim model
        # Takes long to import so only if parsing is needed
        from pysd import read_vensim

        read_vensim(
            str(pysimgame_model_filepath), initialize=False, split_views=True
        )
    elif pysimgame_model_filepath.suffix == ".xmile":
        # Xmile model
        from pysd import read_xmile

        read_xmile(str(pysimgame_model_filepath), initialize=False)
    elif pysimgame_model_filepath.suffix == ".py":
        # Python model
        pass
    else:
        raise ValueError(
            (
                'Impossible to parse "{}".'
                "Model not known. Only accepts .mdl, .py or .xmile files."
            ).format(pysimgame_model_filepath)
        )
    # Now that the file is a python file, we can directly read it
    pysimgame_model_filepath = pysimgame_model_filepath.with_suffix(".py")


def create_initial_conditions_file(game: Game | str):
    """Create the file for inital conditions.

    If the file already exists, the user will be prompted in the terminal.
    """
    game = Game(game)
    if game.INITIAL_CONDITIONS_FILE.exists():
        ans = input("Initial conditions file exist already. Overwrite ? [y/n]")
        if ans not in ["Y", "y", "yes"]:
            return

    # This returns model.components
    model = game.load_model()
    # This retuurns model
    import pysd

    _model = pysd.load(game.PYSD_MODEL_FILE)
    doc = _model.doc()
    constants = list(doc["Py Name"][doc["Type"] == "constant"])

    def valid_component(component_name: str):
        # Check component is valid for initial conditions
        if component_name in [
            "time",
            "final_time",
            "initial_time",
            "saveper",
            "time_step",
        ]:
            return False

        # Constants are accepted
        if component_name in constants:
            print(f"Constant {component_name}")
            return True
        # This will remove components that are function of other components
        #  Code is from PySD and I don't understand it exactly
        if model._dependencies[component_name]:
            deps = list(model._dependencies[component_name])
            if not (len(deps) == 1 and deps[0] in _model.initialize_order):
                print(f"Removed {component_name = }")
                return False
        return True

    initial_conditions = {
        "_time": float(model.time()),
        **{
            region: {
                attr: float(getattr(model, attr)())
                for attr in model._namespace.values()
                if valid_component(attr)
            }
            for region in game.REGIONS_DICT.keys()
        },
    }

    with open(game.INITIAL_CONDITIONS_FILE, "w") as f:
        json.dump(initial_conditions, f, indent=4)


def import_game(
    game_name: str,
    model_filepath: pathlib.Path,
    regions_dict: RegionsDict,
    theme_file: pathlib.Path = None,
    background_file: pathlib.Path = None,
    version: Any = 0,
):
    """Import a new game on computer.

    This create a game from a PySD model file.
    This function should be used as it will check the consistency of the
    games created, though it is also possible to simply modify the files.
    """
    logging.info("Importing new game")
    # Game name
    check_game_name(game_name)
    logging.info("[OK] Game Name")

    # Create the game folder
    game_path = pathlib.Path(PYSDGAME_DIR, game_name)
    game_path.mkdir()
    # Need this to remove the folder we just created if anything goes wrong
    try:
        # PySD file used is parsed and created in game_path
        if model_filepath is None:
            raise FileNotFoundError("A model file must be given.")
        parse_model_file(model_filepath, game_path)
        logging.info("[OK] Model File")

        # Regions are stored in a json file
        regions_filepath = pathlib.Path(game_path, REGIONS_FILE_NAME)
        with open(regions_filepath, "w") as f:
            json.dump(  # A json file with all the regions
                {
                    region.name: region.to_dict()
                    for region in regions_dict.values()
                },
                f,
                indent=4,
            )
        logging.info("[OK] Regions")

        # Creates a dir for backgrounds
        backgrounds_path = pathlib.Path(game_path, BACKGROUND_DIR_NAME)
        backgrounds_path.mkdir()
        ORIGINAL_BACKGROUND_FILEPATH = pathlib.Path(
            backgrounds_path, ORIGINAL_BACKGROUND_FILESTEM
        ).with_suffix(".tga")
        if background_file is not None:
            # Check if we can load the image
            img_surf = image.load(background_file)
            img_size = img_surf.get_size()
            # save the original image
            # Regions will have been set for the original size
            image.save(img_surf, ORIGINAL_BACKGROUND_FILEPATH)
            # Save the original size of the picture
            image.save(
                img_surf,
                ORIGINAL_BACKGROUND_FILEPATH.with_stem(
                    "{}x{}".format(*img_size)
                ),
            )
        logging.info("[OK] Background")

        # Other parameters that can be changed in the game but could be defaulted
        game_settings = {
            "theme_file": theme_file,
            "Resolution": PYSDGAME_SETTINGS["Resolution"]
            if background_file is None
            else img_size,
            # Whether the game has only one region
            "SingleRegion": len(regions_dict) == 1,
            # Version of pysimgame
            "pysimgame.__version__": pysimgame.__version__,
            # Version of the game
            "{}.__version__".format(game_name): version,
        }
        with open(pathlib.Path(game_path, GAME_SETTINGS_FILENAME), "w") as f:
            json.dump(game_settings, f)
        logging.info("[OK] Game Settings")
    except Exception as exp:
        # Remove useless created files if an error occured
        shutil.rmtree(game_path)
        raise exp
