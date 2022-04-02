"""Pysdgame module."""


__version__ = 0


DEV_MODE = True  # TODO: change false on production

import logging

LOGGING_LEVEL = logging.INFO

import os
import contextlib

with open(os.devnull, "w") as f, contextlib.redirect_stdout(f):
    import pygame

from .events import *
from .utils.directories import PYSDGAME_DIR
from .utils.pysimgame_settings import PYSDGAME_SETTINGS
