"""Pysdgame module."""
import logging

__version__ = 0
DEV_MODE = True  # TODO: change false on production

# Logging parameters
console = logging.StreamHandler()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.getLogger().addHandler(console)

from .utils.directories import PYSDGAME_DIR
from .utils.pysdgame_settings import PYSDGAME_SETTINGS
