import logging

import pysdgame

# Logging parameters
formatter = logging.Formatter(
    "%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s"
)
console = logging.StreamHandler()
console.setFormatter(formatter)

logger = logging.getLogger(pysdgame.__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(console)
