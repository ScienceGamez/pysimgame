"""Utility functions for handling directories."""
import os
import pathlib
import pysdgame

from pysdgame.types import FilePath

# TODO: check for linux and macos
_app_data_dir = os.environ["APPDATA"]

PYSDGAME_DIR = pathlib.PurePath(_app_data_dir, "pysdgame")

# Themes can be shared across the different games
THEMES_DIR = os.path.join(PYSDGAME_DIR, "themes")
DEFAULT_THEMES_DIR = os.path.join(*pysdgame.__path__, "themes")

SETTINGS_DIR = os.path.join(PYSDGAME_DIR, "settings")

DESKTOP_DIR = os.path.join(os.path.join(os.environ["USERPROFILE"]), "Desktop")

REGIONS_FILE_NAME = "regions.json"
THEME_FILENAME = "theme.json"
MODEL_FILESTEM = "model"
BACKGROUND_DIR_NAME = "backgrounds"
ORIGINAL_BACKGROUND_FILESTEM = "orginal"
GAME_SETTINGS_FILENAME = "settings.json"


# Creates the pysdgame dir if not created
if not os.path.isdir(PYSDGAME_DIR):
    os.mkdir(PYSDGAME_DIR)
if not os.path.isdir(THEMES_DIR):
    os.mkdir(THEMES_DIR)


def find_theme_file(theme_filename: FilePath) -> FilePath:
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
