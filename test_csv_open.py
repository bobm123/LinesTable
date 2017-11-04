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
import json
import logging
import os

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


def get_all_axis(table, axis):
    ''' return all rows with a specific axis (width, height, length)
    in a dictionary and set 'name' as the key '''
    selected = {r[1]:r[2:] for r in table if axis in r[0]}
    return selected


def is_valid(point):
    return all(isinstance(w, float) for w in point)


def remove_invalid(plist, replace=None):
    if replace == None:
        return [p for p in plist if is_valid(p)]
    else:
        return [p if is_valid(p) else replace for p in plist]


def generate_sections(offset_table):
    '''Generate the cross sections in 3D at each station
    from the given lines and organizes the lines into coordinates
    (x, y, z) = (width, height length). Returns each as a list
    contained in a dictionary'''

    # Have a dictionary with line names for keys, list of points for values
    line_order = ['coaming', 'gunwale', 'sheer', 'chine', 'bottom', 'skeg']
    sections = []
    for line_name in line_order:
        if line_name in offset_table:
            sections.append(offset_table[line_name])

    sections = list(map(list, zip(*sections)))
    return sections


def offset_reader(args):
    """ parse the csv expected offset table fields """
    logger.info("arguments" + str(args))
    with open(args.filename, 'r') as csvfile:
        raw_table = list(csv.reader(csvfile, delimiter=',', quotechar='"'))

    logger.info('original table:')
    for i, row in enumerate(raw_table):
        logger.info (f'row {i}: {row}')

    # Remove comments lines
    offset_table = [r for r in raw_table if not r[0].startswith('#')]

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

    # Break out each set of dimension and recombine as (x,y,z)
    ot_widths = get_all_axis(offset_table, 'width')
    ot_heights = get_all_axis(offset_table, 'height')
    ot_lengths = get_all_axis(offset_table, 'length')

    ot_combined = {}
    for line_name in ot_widths:
        x = ot_widths[line_name]
        y = ot_heights[line_name]
        z = [float(zs) for zs in ot_lengths['station']]
        line_points = remove_invalid(list(zip(x, y, z)), [])
        ot_combined[line_name] = line_points

    return ot_combined


def main(args):
    offset_table = offset_reader(args)

    offset_table['sections'] = generate_sections(offset_table)

    out_filename, _ = os.path.splitext(args.filename)
    out_filename = out_filename + '.json'
    logger.debug('writing json data:\n' + json.dumps(offset_table))
    with open(out_filename, 'w') as opf:
        json.dump(offset_table, opf)


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
