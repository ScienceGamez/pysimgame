"""Argument parsing for pysimgame.

Capabilities:
    * start an existing game
    * initialize a new game
    * manage existant games
"""
import argparse
from pathlib import Path
import sys

import git
import pysimgame

from pysimgame.game import (
    Game,
    GameAlreadyExistError,
    GameNotFoundError,
    guess_game_name_from_clone_arg,
    list_available_games,
)
from pysimgame.utils.directories import REPOSITORY_URL
from pysimgame.game_manager import GameManager


def create_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(prog="pysimgame")
    parser.add_argument(
        "--list",
        action="store_true",
        help="List the current available games.",
    )
    parser.add_argument(
        "game",
        nargs="?",
        type=str,
        default="",
        help="Name of the game to start",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="If specified, this will initialize the game",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete the game",
    )
    parser.add_argument(
        "--clone",
        nargs=1,
        type=str,
        help=(
            "The game that should be downloaded.\n"
            "\tIf link will try to download from that link.\n"
            "\tIf str will try to download from the official repository.\n"
        ),
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help=("Push the game on the registered repository."),
    )
    parser.add_argument(
        "--publish",
        nargs=1,
        type=str,
        help=("Publish the game on the specified repository."),
    )
    parser.add_argument(
        "--readme",
        action="store_true",
        help=("Generate a readme if it does not exist for the game."),
    )
    parser.add_argument(
        "--dir",
        nargs="?",
        type=str,
        default="",
        help="The directory where the game is located.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Return the version of the selected game.",
    )

    parser.add_argument(
        "--log",
        "--verbose",
        nargs="?",
        type=int,
        default=20,
        help=(
            "The level of logging to use by default "
            "(10 = DEBUG, 40=ONLY_ERROR_)."
            "More choices available at "
            "https://docs.python.org/3/library/logging.html#logging-levels. "
            "Using 20 by default."
        ),
        metavar="LEVEL",
    )

    return parser


def _parse_no_game(args):
    """Special parsing when no game is present."""
    if args.list:
        dir_arg = [] if not args.dir else [Path(args.dir)]
        for game in list_available_games(*dir_arg):
            print(game, "" if not args.version else game.VERSION)

    elif args.version:
        print(f"pysimgame={pysimgame.__version__}")


def read_parsed_args(args):
    """Read the args parsed by the parser."""
    if args.clone:
        if not args.init:
            # Cloning is the same as init
            args.init = True
        if not args.game:
            # Guess the name of the game
            clone = args.clone[0]
            args.game = guess_game_name_from_clone_arg(clone)
            # Ensure the game will be created

    if not args.game:
        _parse_no_game(args)
        sys.exit(0)

    try:
        game_dir = args.dir or None
        game = Game(
            args.game,
            create=args.init,
            game_dir=game_dir,
            remote="" if not args.clone else args.clone[0],
        )
    except GameNotFoundError or GameAlreadyExistError as gnf_err:
        print(gnf_err.msg)
        sys.exit(1)

    if args.version:
        print(game.VERSION)
        sys.exit(0)
    if args.readme:
        game.add_readme()
        print(f"Added {Path(game.GAME_DIR, 'README.md')}")
        sys.exit(0)
    if args.delete:

        if (
            input(
                f"You are going to delete all the data for {game}. \n"
                f"Type '{args.game}' to confirm."
            )
            == args.game
        ):
            game._allow_delete = True
            game.delete()
            sys.exit(0)

        else:
            print("Did not delete {asdf} . ")
            sys.exit(1)

    if args.push:
        print("pushing the game")
        game.push_game()
        sys.exit(0)

    if args.publish:
        if input(
            f"You are going to publish {game} from {game.GAME_DIR} "
            f"to {args.publish[0]}\n"
            "Do you want to continue ? [Y/n] "
        ) in ["Y", "y"]:
            game.publish_game(args.publish[0])
            print(f"{game} published.")
            sys.exit(0)
        else:
            print("Abort.")
            sys.exit(1)

    # Still not existed yet, we start the game
    # TODO: think about how we want to start the game,
    # New design ? refactor ?
    GAME_MANAGER = GameManager()
    GAME_MANAGER.start_new_game(game)
