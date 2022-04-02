"""Main entry script.

Capabilities:
    * start an existing game
    * initialize a new game
"""
import argparse

parser = argparse.ArgumentParser(prog="pysimgame")
parser.add_argument("--foo", help="foo help")
args = parser.parse_args()
