#!/usr/bin/env python

"""
Command line interface to mini-project
"""

import argparse
from mini_project import Rack

def parse_command_line():
    "parses args for the mini-project function"
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--num", help="Change number of animals to simulate inventory", dest= 'num_salamanders', type=int, default=50 )
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument(
        "-m", "--move", nargs=2, metavar=("ANIMAL_ID", "TARGET_RACK"),
        help="Move a salamander to a new rack (e.g. SAL_001 Rack 2)")
    args = parser.parse_args()
    return args
    

    ## add long args example from hack-9-python
    #parser.add_argument(
    #    "--next",
    #    help="returns a countdown until the next Darwin Day",
    #    action="store_true")

    ## check that user only entered one action arg
    #if sum([args.next, args.last, args.info]) > 1:
    #    raise SystemExit(
    #        "only one of 'next', 'last' or 'info' at a time.")
    #return args


def main():
    "run main function on parsed args"
    # get arguments from command line as a dict-like object
    args = parse_command_line()
    R = Rack(num_salamanders = args.num)
    R.inventory

    if args.move:
        animal_id, target_rack = args.move
        R.move_salamander([animal_id], target_rack)

    if args.verbose:
        print(R.inventory)

    
    # example to pass arguments to call functions
    #if args.next:
    #    birthday('next')
    #elif args.last:
    #    birthday('last')
    #elif args.info:
    #    info()

if __name__ == "__main__":
    main()