#!/usr/bin/env python3
'''
Generates a set of points defining the "lines" and sections
of a boat hull given a table of offsets.
'''

__author__ = "Robert marchese"
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
    '''Convets dimenstion from feet-inches-eigths to decimal inches'''

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
    '''return all rows with a specific axis (width, height, length)
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


def parse_csv_offsets(args):
    ''' parse the csv expected offset table fields '''
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


def rotate_point(cy, cz, angle, p):
    '''rotate by an angle around a point in the yz-plane'''
    s = sin(angle)
    c = cos(angle)

    # translate point back to origin:
    p[1] -= cy
    p[2] -= cz

    # rotate point
    ynew = p[2] * s + p[1] * c
    znew = p[2] * c - p[1] * s

    # translate point back:
    p[1] = ynew + cy
    p[2] = znew + cz

    return p;


# TODO: Move this operation to F360 scripts
def rake_angle(offsets, st_index, angle):
    xc_original = offsets['sections'][st_index]
    logger.debug("original section " + str(st_index) + " points\n" + str(xc_original))

    # Angle is givent in degrees from the baseline
    angle = radians(angle - 90)

    # Assume angle taken at top of section
    y0 = xc_original[0][1]
    z0 = xc_original[0][2]

    # Apply rotation in xz plane around y = y0 to sections
    xc_new = []
    for pt in xc_original:
        pt = list(pt)
        pt = rotate_point(y0, z0, angle, pt)
        xc_new.append(pt)
    offsets['sections'][st_index] = xc_new

    logger.debug("modified section " + str(st_index) + " points\n" + str(xc_new))

    # Apply rotation in xz plane around y = y0 to lines
    for name,coords in offsets['lines'].items():
        if coords[st_index]:
            logger.debug("modifying " + str(name) + " at station " + str(st_index))
            pt = list(coords[st_index])
            pt = rotate_point(y0, z0, angle, pt)
            coords[st_index] = pt
        else:
            logger.debug("ignoring " + str(name) + " at station " + str(st_index))

    return offsets 


def offset_reader(args):

    # Read the lines from an offset table
    offset_data = parse_csv_offsets(args)

    # Add a set of cross sections
    offset_data['sections'] = generate_sections(offset_data)

    # Apply optional rake angles at bow and transom
    # TODO: Move this operation to F360 scripts
    bindex = 0
    offset_data = rake_angle(offset_data, bindex, args.bow_angle)
    tindex = len(offset_data['sections']) - 1
    offset_data = rake_angle(offset_data, tindex, args.transom_angle)

    out_filename, _ = os.path.splitext(args.filename)
    out_filename = out_filename + '.json'
    logger.debug('writing json data:\n' + json.dumps(offset_data))
    with open(out_filename, 'w') as opf:
        json.dump(offset_data, opf)


if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("filename", help="input .csv file (offset table)")

    # Optional arguments that require a parameter
    parser.add_argument("-b", "--bow", action="store", 
        dest="bow_angle", default=90,
        help="Angle of the bow measured from the baseline ")

    parser.add_argument("-t", "--transom", action="store", 
        dest="transom_angle", default=90,
        help="Angle of the transom measured from the baseline")

    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    offset_reader(args)
