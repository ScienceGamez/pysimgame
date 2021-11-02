"""Load the pysdgame settings.

Check using the version if the file must be updated.
"""
import json
import os
import shutil

import pysdgame
from pysdgame.utils import recursive_dict_missing_values

from .directories import PYSDGAME_DIR


# Check the settings exist or copy them
SETTINGS_DIR = os.path.join(PYSDGAME_DIR, "settings")
if not os.path.isdir(SETTINGS_DIR):
    os.mkdir(SETTINGS_DIR)

SETTINGS_FILE = os.path.join(SETTINGS_DIR, "pysdgame_settings.json")
THEME_FILE = os.path.join(SETTINGS_DIR, "pysdgame_settings.json")


# The default file is in the same folder as this python script
# It comes with the library distribution
DEFAULT_FILE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SETTINGS_FILE = os.path.join(
    DEFAULT_FILE_DIR, "pysdgame_settings.json"
)

if not os.path.isfile(SETTINGS_FILE):
    # Copy the file to the new location if it does not exist
    shutil.copyfile(DEFAULT_SETTINGS_FILE, SETTINGS_FILE)


# Settings file should exists now
with open(SETTINGS_FILE) as f:
    PYSDGAME_SETTINGS = json.load(f)


def save_pysdgame_settings():
    """Save the settings in the file."""
    with open(SETTINGS_FILE) as f:
        json.dump(PYSDGAME_SETTINGS, f)


if "__version__" in PYSDGAME_SETTINGS:
    if pysdgame.__version__ > PYSDGAME_SETTINGS["__version__"]:
        # Updates the new parameters
        # Update settings that don't exist
        with open(DEFAULT_SETTINGS_FILE) as f:
            DEFAULT_SETTINGS = json.load(f)
        print(PYSDGAME_SETTINGS)
        # Updates only the missing values to save user preferences
        recursive_dict_missing_values(DEFAULT_SETTINGS, PYSDGAME_SETTINGS)
        # Change to the new version
        PYSDGAME_SETTINGS["__version__"] = pysdgame.__version__
        print(PYSDGAME_SETTINGS)
        save_pysdgame_settings()
