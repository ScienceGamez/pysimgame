"""Utility functions for handling directories."""
import os
import pathlib

import pysimgame

# TODO: check for linux and macos
if "APPDATA" in os.environ:
    app_data_dir = os.environ["APPDATA"]
    PYSDGAME_DIR = pathlib.Path(app_data_dir, "pysimgame")
else:
    # Not windows
    PYSDGAME_DIR = pathlib.Path(pathlib.Path.home(), ".pysimgame")


# Themes can be shared across the different games
THEMES_DIR = os.path.join(PYSDGAME_DIR, "themes")
DEFAULT_THEMES_DIR = os.path.join(*pysimgame.__path__, "themes")

SETTINGS_DIR = os.path.join(PYSDGAME_DIR, "settings")

TEST_DIR = pathlib.Path(*pysimgame.__path__, "..", "tests")
EXAMPLES_DIR = pathlib.Path(*pysimgame.__path__, "..", "examples")

SCIENCEGAMEZ_URL = "https://github.com/ScienceGamez/"
REPOSITORY_URL = "https://github.com/ScienceGamez/"
PYSIMGAME_GITHUB_URL = SCIENCEGAMEZ_URL + "pysimgame"
READTHEDOCS_URL = "https://pysimgame.readthedocs.io/en/latest/"
# DESKTOP_DIR = os.path.join(os.path.join(os.environ["USERPROFILE"]), "Desktop")

REGIONS_FILE_NAME = "regions.json"
THEME_FILENAME = "theme.json"
MODEL_FILESTEM = "model"
MODEL_FILENAME = MODEL_FILESTEM + ".py"
INITIAL_CONDITIONS_FILENAME = "initial_conditions.json"
BACKGROUND_DIR_NAME = "backgrounds"
ORIGINAL_BACKGROUND_FILESTEM = "orginal"
GAME_SETTINGS_FILENAME = "settings.json"

FORBIDDEN_GAME_NAMES = [
    "settings",
    "themes",
    "__pycache__",
    ".git",
    "pysimgame",
]

# Creates the pysimgame dir if not created
if not os.path.isdir(PYSDGAME_DIR):
    os.mkdir(PYSDGAME_DIR)
if not os.path.isdir(THEMES_DIR):
    os.mkdir(THEMES_DIR)


def find_theme_file(theme_filename: pathlib.Path) -> pathlib.Path:
    """Find the real address of a theme file from the given one.

    First check if the user has the file in his themes.

    :param theme_file_path: The name of the file to look for.
    :return: A file path that exists with correct theme.
    """
    # Tries in the themes file from appdata
    data_theme_file_path = os.path.join(THEMES_DIR, theme_filename)
    if os.path.isfile(data_theme_file_path):
        return data_theme_file_path
    else:
        # Tries the default path
        return os.path.join(DEFAULT_THEMES_DIR, "default.json")
