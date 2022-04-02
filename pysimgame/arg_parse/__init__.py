"""Argument parsing for pysimgame.

Capabilities:
    * start an existing game
    * initialize a new game
    * manage existant games
"""
import argparse
import sys

from pysimgame.game import Game, GameNotFoundError, list_available_games


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


def _parse_no_game(args):
    if args.list:
        for game in list_available_games():
            print(game)


def parse_args(args):
    if not args.game:
        _parse_no_game(args)
        sys.exit(0)

    try:
        game = Game(args.game, create=args.init, game_dir=args.dir)
    except GameNotFoundError as gnf_err:
        print(gnf_err.msg)
        sys.exit(1)

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

        else:
            print("Did not delete {asdf} . ")
