#!/usr/bin/env python3
"""
Attempt to process an offsets table w/o using pandas
for easier integration into Fusion360 API
"""

__author__ = "Your Name"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import csv
import logging


# Setup Logging
logger = logging.getLogger('csv test')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('test_csv_open.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG) #change to ERROR or WARNING after deplot
log_fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_short_fmt = logging.Formatter('%(levelname)s - %(message)s')
fh.setFormatter(log_fmt)
ch.setFormatter(log_short_fmt)
logger.addHandler(fh)
logger.addHandler(ch)
# Setup Logging


def fie_to_di(d):
    '''Convets dimenstion in feet-inches-eigths to decimal inches'''

    if isinstance(d, str):
        fie = d.split('-')
    else:
        return d

    #TODO: fie[1] in range(0,12), fie[2] in range(0,8)
    if len(fie) == 3:
        return 12*float(fie[0])+float(fie[1])+float(fie[2])/8.0
    else:
        return d



def offset_reader(args):
    """ parse the csv expected offset table fields """
    logger.info("arguments" + str(args))
    with open(args.filename, 'r') as csvfile:
        offset_table = list(csv.reader(csvfile, delimiter=',', quotechar='"'))

    logger.info('original table:')
    for i, row in enumerate(offset_table):
        logger.info (f'row {i}: {row}')

    # TODO: definitly 'happy path' coding here, so need to deal with
    # unexpected table formats.

    #logger.info(f'header row is\n{offset_table[0]}')

    # force rows to lower case
    for i,row in enumerate(offset_table):
        offset_table[i] = [str.lower(x) for x in row]

    # replicate 'dittos' in axis column
    current = ''
    for i,row in enumerate(offset_table):
        if row[0] and not current == row[0]:
            current = row[0]
        else:
            row[0] = current
        offset_table[i][0] = current

    # convert feet-inches-eights to decimal inches
    for i,row in enumerate(offset_table):
        offset_table[i] = [fie_to_di(x) for x in row]

    logger.info('modified table:')
    for i, row in enumerate(offset_table):
        logger.info (f'row {i}: {row}')




def main(args):
    offset_reader(args)


if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("filename", help="input .csv file (offset table)")

    # Optional argument flag which defaults to False
    parser.add_argument("-f", "--flag", action="store_true", default=False)

    # Optional argument which requires a parameter
    parser.add_argument("-b", "--butt", action="store", dest="buttocks_lines", help="list of buttocks line distances from cl")
    parser.add_argument("-w", "--water", action="store", dest="water_lines", help="list of water line distances from from base")

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity (-v, -vv, etc)")

    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)
