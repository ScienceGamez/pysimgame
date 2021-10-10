"""Utility functions for handling directories."""
import os

# TODO: check for linux and macos
_app_data_dir = os.environ['APPDATA']

PYSDGAME_DIR = os.path.join(_app_data_dir, 'pysdgame')

# Creates the pysdgame dir if not created
if not os.path.isdir(PYSDGAME_DIR):
    os.mkdir(PYSDGAME_DIR)
