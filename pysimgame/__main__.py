"""Main entry script.


"""
import argparse

import pysimgame.arg_parse


parser = pysimgame.arg_parse.create_parser()
args = parser.parse_args()

if not args.game and not args.list:
    parser.print_usage()

pysimgame.arg_parse.read_parsed_args(args)
