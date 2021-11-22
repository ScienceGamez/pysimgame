"""Module for creating new games."""
import json
import pathlib
import shutil
import logging
from typing import Any
from black import path_empty

from numpy import True_
import pygame
from pygame import image
import pysdgame
from pysdgame import logger

from pysdgame.types import RegionsDict
from pysdgame.utils.images import resize_image
from pysdgame.utils.pysdgame_settings import PYSDGAME_SETTINGS, SETTINGS_FILE

from .utils.directories import (
    BACKGROUND_DIR_NAME,
    GAME_SETTINGS_FILENAME,
    MODEL_FILESTEM,
    ORIGINAL_BACKGROUND_FILESTEM,
    PYSDGAME_DIR,
    REGIONS_FILE_NAME,
    THEME_FILENAME,
)


def error_popup(msg: str):
    return


def check_game_name(name: str) -> None:
    # Check that it already exist
    dir = pathlib.Path(PYSDGAME_DIR)
    if name == "":
        raise ValueError("Game name cannot be empty.")
    existing_games = [d.name for d in dir.iterdir()]
    logger.debug("Found games : {}".format(existing_games))
    if name in existing_games:
        raise ValueError("Name '{}' is already taken.".format(name))


def from_local_file(
    name: str,
    model_file: pathlib.Path,
    theme_file: pathlib.Path = None,
) -> None:
    return


def parse_model_file(model_filepath: pathlib.Path, game_path: pathlib.Path):
    """Read the model file and parse it into python script using pysd."""
    # Where pysdgame will store the model

    pysdgame_model_filepath = pathlib.Path(
        game_path, MODEL_FILESTEM + model_filepath.suffix
    )

    shutil.copyfile(  # Copy to the new location
        model_filepath, pysdgame_model_filepath
    )

    # Check which model type it is to parse it
    if pysdgame_model_filepath.suffix == ".mdl":
        # Vensim model
        # Takes long to import so only if parsing is needed
        from pysd import read_vensim

        read_vensim(
            str(pysdgame_model_filepath), initialize=False, split_views=True
        )
    elif pysdgame_model_filepath.suffix == ".xmile":
        # Xmile model
        from pysd import read_xmile

        read_xmile(str(pysdgame_model_filepath), initialize=False)
    elif pysdgame_model_filepath.suffix == ".py":
        # Python model
        pass
    else:
        raise ValueError(
            (
                'Impossible to parse "{}".'
                "Model not known. Only accepts .mdl, .py or .xmile files."
            ).format(pysdgame_model_filepath)
        )
    # Now that the file is a python file, we can directly read it
    pysdgame_model_filepath = pysdgame_model_filepath.with_suffix(".py")


def import_game(
    game_name: str,
    model_filepath: pathlib.Path,
    regions_dict: RegionsDict,
    theme_file: pathlib.Path = None,
    background_file: pathlib.Path = None,
    version: Any = 0,
):
    """Import a new game on computer.

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
            # Version of pysdgame
            "pysdgame.__version__": pysdgame.__version__,
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
