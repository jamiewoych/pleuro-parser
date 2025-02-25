#!/usr/bin/env python

"""
Command line interface to mini-project
"""

import argparse
#from mini-project import functions


def parse_command_line():
    "parses args for the mini-project function"

    # init parser and add arguments
    parser = argparse.ArgumentParser()

    ## add long args example from hack-9-python
    #parser.add_argument(
    #    "--next",
    #    help="returns a countdown until the next Darwin Day",
    #    action="store_true")

    ## parse args
    args = parser.parse_args()

    ## check that user only entered one action arg
    #if sum([args.next, args.last, args.info]) > 1:
    #    raise SystemExit(
    #        "only one of 'next', 'last' or 'info' at a time.")
    return args


def main():
    "run main function on parsed args"

    # get arguments from command line as a dict-like object
    args = parse_command_line()

    # example to pass arguments to call functions
    #if args.next:
    #    birthday('next')
    #elif args.last:
    #    birthday('last')
    #elif args.info:
    #    info()


if __name__ == "__main__":
#    birthday('next')
#    info()
