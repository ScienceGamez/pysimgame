"""Load the pysimgame settings.

Check using the version if the file must be updated.
"""
import json
import os
import shutil
from typing import Any, Dict

import pysimgame
from pysimgame.utils import recursive_dict_missing_values
from pysimgame.utils.logging import logger

from .directories import (
    DEFAULT_THEMES_DIR,
    SETTINGS_DIR,
    THEMES_DIR,
)


# Check the settings exist or copy them

if not os.path.isdir(SETTINGS_DIR):
    os.mkdir(SETTINGS_DIR)

SETTINGS_FILE = os.path.join(SETTINGS_DIR, "pysimgame_settings.json")


# The default file is in the same folder as this python script
# It comes with the library distribution
DEFAULT_SETTINGS_FILE = os.path.join(
    *pysimgame.__path__, "utils", "pysimgame_settings.json"
)

logger.debug(f"PYSDGAME SETTING FILE: {DEFAULT_SETTINGS_FILE}")


if not os.path.isfile(SETTINGS_FILE):
    # Copy the file to the new location if it does not exist
    shutil.copyfile(DEFAULT_SETTINGS_FILE, SETTINGS_FILE)


# Settings file should exists now
with open(SETTINGS_FILE) as f:
    PYSDGAME_SETTINGS: Dict[str, Any] = json.load(f)


logger.debug(f"PYSDGAME SETTING : {PYSDGAME_SETTINGS}")


def save_pysimgame_settings():
    """Save the settings in the file."""
    with open(SETTINGS_FILE) as f:
        json.dump(PYSDGAME_SETTINGS, f)


if pysimgame.__version__ > PYSDGAME_SETTINGS["__version__"]:
    # Updates the new parameters
    # Update settings that don't exist
    with open(DEFAULT_SETTINGS_FILE) as f:
        DEFAULT_SETTINGS = json.load(f)
    # Updates only the missing values to save user preferences
    recursive_dict_missing_values(DEFAULT_SETTINGS, PYSDGAME_SETTINGS)
    # Change to the new version
    PYSDGAME_SETTINGS["__version__"] = pysimgame.__version__
    save_pysimgame_settings()
    # Copy the themes files
    shutil.copytree(DEFAULT_THEMES_DIR, THEMES_DIR, dirs_exist_ok=True)


elif pysimgame.DEV_MODE:
    # Copy the file if we are developping
    shutil.copyfile(DEFAULT_SETTINGS_FILE, SETTINGS_FILE)
    # Copy the themes files
    shutil.copytree(DEFAULT_THEMES_DIR, THEMES_DIR, dirs_exist_ok=True)
