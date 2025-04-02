#!/usr/bin/env python

"""
Command line interface to mini-project
"""

import argparse
import pandas as pd
from mini_project import Rack

def parse_command_line():
    "parses args for the mini-project function"
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--num",
        help="Change number of animals to simulate inventory",
        dest= 'num_salamanders',
        type=int, default=50)
    parser.add_argument(
        "-m", "--move",
        nargs=2, metavar=("animal_id", "target_rack"),
        help="Move a salamander to a new rack (e.g. SAL_001 Rack 2)")
    parser.add_argument("-e", "--euth", help="remove animal from inventory and report to euthanasia log",
        nargs=7, metavar=("animal_id", "dod", "weight", "sex", "purpose", "experimenter", "complications"))
    parser.add_argument(
        "-v", "--verbose",
         help="increase output verbosity",
         action="store_true")
    parser.add_argument(
        "-f", "--file",
        help="Path to existing salamander inventory CSV",
        type=str, default=None)
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
    R = Rack(args.num_salamanders)
    R.inventory
    
    
    
    if args.verbose:
        print(f"arguments = {args}")

    if args.file:
        # Load existing inventory CSV
        print(f"Loading inventory from {args.file}...")
        R = Rack()
        R.inventory = pd.read_csv(args.file)
    else:
        # Generate a new inventory
        R = Rack(args.num_salamanders)
    
    if args.move:
        animal_id, target_rack = args.move
        R.move_salamander([animal_id], target_rack)

    if args.euth:
        animal_id, dod, weight, sex, purpose, experimenter, complications = args.euth
        euth_file = "euthanasia_file.csv"
        R.euthanize_animal(animal_id, dod, weight, sex, purpose, experimenter, complications)
        R.euthanasia_log
        R.euthanasia_log = pd.DataFrame(R.euthanasia_log)
        R.euthanasia_log.to_csv(euth_file, index=False)
        print("Changes saved to 'salamander_inventory.csv' and 'euthanasia_log.csv'.")

    if args.verbose:
        print(R.inventory)
    
    output_file = "salamander_inventory.csv"
    R.inventory.to_csv(output_file, index=False)

    if args.verbose:
        print("Updated Inventory:")
        print(R.inventory.head())


    print(f"Inventory saved to {output_file}")
    
    return R
    
    
    # example to pass arguments to call functions
    #if args.next:
    #    birthday('next')
    #elif args.last:
    #    birthday('last')
    #elif args.info:
    #    info()

if __name__ == "__main__":
    main()