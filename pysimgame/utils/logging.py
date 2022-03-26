import configparser
import functools
import importlib.util
import json
import logging
import logging.config
from pathlib import Path
from typing import Callable

import pygame
import pysimgame
from pygame_gui.ui_manager import UIManager
from pygame_gui.windows import UIMessageWindow

from .directories import PYSDGAME_DIR
from .pysimgame_settings import PYSDGAME_SETTINGS

# Find the logging config file
if "logging_config" not in PYSDGAME_SETTINGS:
    PYSDGAME_SETTINGS["logging_config"] = Path(
        PYSDGAME_DIR, "logging_config.json"
    )


class _LOGGING_CONFIG(dict):
    def __init__(self):
        super().__init__(
            {
                "version": 1,
                "formatters": {
                    "default": {
                        "class": "logging.Formatter",
                        "format": (
                            "%(asctime)s %(threadName)-10s %(name)s "
                            "%(levelname)-8s %(message)s"
                        ),
                    },
                    "location": {
                        "class": "logging.Formatter",
                        "format": (
                            "%(asctime)s %(threadName)-10s %(name)s "
                            "%(levelname)-8s %(message)s \n"
                            '"%(pathname)s", line %(lineno)d, in %(module)s %(funcName)s'
                        ),
                    },
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "level": "INFO",
                        "formatter": "default",
                    },
                    "debug": {
                        "class": "logging.StreamHandler",
                        "level": "DEBUG",
                        "formatter": "location",
                    },
                },
                "loggers": {},
                "root": {
                    "level": "DEBUG",
                    "handlers": ["console"],
                },
            }
        )

    def save(self):
        """Save the logging config."""
        LOGGING_FILE = Path(PYSDGAME_SETTINGS["logging_config"])
        with LOGGING_FILE.open("w") as f:
            json.dump(self, f)

    def load(self):
        """Load the config form the file."""
        LOGGING_FILE = Path(PYSDGAME_SETTINGS["logging_config"])
        print(f"Loading config {LOGGING_FILE} .")
        with LOGGING_FILE.open("r") as f:
            LOGGING_CONFIG = json.load(f)

        super().__init__(LOGGING_CONFIG)
        logging.config.dictConfig(LOGGING_CONFIG)


LOGGING_CONFIG = _LOGGING_CONFIG()

LOGGING_CONFIG.save()
LOGGING_CONFIG.load()


def register_logger(logger: logging.Logger):
    """Add a logger to pysimgame logging settings.

    :param logger: The logger object to register.
    """
    if logger.name not in LOGGING_CONFIG["loggers"]:
        LOGGING_CONFIG["loggers"][logger.name] = {
            "level": logger.getEffectiveLevel(),
            "handlers": ["console", "debug"],
        }
    LOGGING_CONFIG.save()


def logger_enter_exit(
    level: int = logging.DEBUG,
    with_args: bool = False,
    with_return: bool = False,
    ignore_enter: bool = False,
    ignore_exit: bool = False,
) -> Callable:
    """Decorate a function for logging when the function start and ends.

    Can also handle loggin the args and the return values.

    :param level: The level of logging to use, defaults to logging.DEBUG
    :param with_args: Whether to log args as well, defaults to False
    :param with_return: Whether to log return as well, defaults to False
    :param ignore_enter: Whether to ignore the enter statement, defaults to False
    :param ignore_exit: Whether to ignore the exit statement, defaults to False
    :return: the decorated function
    """

    def decorator(func: Callable):
        logger = logging.getLogger(func.__name__)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not ignore_enter:
                logger.log(
                    level,
                    f"[ENTER] {func.__module__}.{func.__name__} "
                    + (f"Args: {args}, Kwargs: {kwargs}" if with_args else ""),
                )
            ret = func(*args, **kwargs)
            if not ignore_exit:
                logger.log(
                    level,
                    f"[EXIT] {func.__module__}.{func.__name__} "
                    + (f"Return: {ret}" if with_return else ""),
                )
            return ret

        return wrapper

    return decorator


class PopUpHandler(logging.Handler):
    def __init__(
        self, ui_manager: UIManager, rect: pygame.Rect = None
    ) -> None:
        super().__init__()
        self.ui_manager = ui_manager
        if rect is None:
            x, y = self.ui_manager.window_resolution
            self.rect = pygame.Rect(x / 3, y / 3, x / 3, y / 3)
        elif isinstance(rect, pygame.Rect):
            self.rect = rect
        else:
            raise TypeError(
                f"rect kwarg must be pygame.Rect, not {type(rect)}."
            )

    def emit(self, record: logging.LogRecord) -> None:
        window = UIMessageWindow(
            self.rect,
            html_message=record.msg,
            manager=self.ui_manager,
            window_title="",
        )
