#! /usr/bin/env -S python3 -B
# coding: utf-8

"""
    This is a basic Python script tempate
    It can be used as a starting point for creating new scrpts
"""

import argparse
import logging
import sys

# configure command-line arguements
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="count", default=0)
args = parser.parse_args()

# configure logging level based on command line arguments
if args.verbose == 0:
    logging_level = logging.WARNING
elif args.verbose == 1:
    logging_level = logging.INFO
else:
    logging_level = logging.DEBUG

logging.basicConfig(level=logging_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", stream=sys.stdout)
logger = logging.getLogger(__name__)

def main(argv):
    """
    The main function that runs when the script is executed
    :return: 0 if script excecuted successfully, non-zero otherwise 
    """
    logger.info(f"Arguments passed: {argv}")
    # add your code here

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
