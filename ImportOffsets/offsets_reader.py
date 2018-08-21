# -*- coding: utf-8 -*-

"""
Generates a set of points defining the 'lines' and sections
of a boat hull given a table of offsets.
"""

__author__ = "Robert Marchese"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import csv
import json
import logging
from math import radians, sin, cos
import os

# Setup Logging
logger = logging.getLogger('offsets reader')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('offsets_reader.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()

# change to ERROR or WARNING after deplot
ch.setLevel(logging.DEBUG)
log_fmt = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s')
log_short_fmt = logging.Formatter('%(levelname)s - %(lineno)d - %(message)s')
fh.setFormatter(log_fmt)
ch.setFormatter(log_short_fmt)
logger.addHandler(fh)
logger.addHandler(ch)


def fie_to_di(d):
    '''Converts a dimension d from feet-inches-eigths to decimal inches'''

    if isinstance(d, str):
        fie = d.split('-')
    else:
        return d

    # TODO: fie[1] in range(0,12), fie[2] in range(0,8)
    if len(fie) == 3:
        return 12*float(fie[0])+float(fie[1])+float(fie[2])/8.0
    else:
        return d


def get_all_axis(table, axis):
    '''return all rows with a specific axis (width, height, length)
    in a dictionary and set 'name' as the key '''
    selected = {r[1]: r[2:] for r in table if axis in r[0]}

    return selected


def is_valid(point):
    if point:
        return all(isinstance(w, float) for w in point)
    else:
        return False


def remove_invalid(plist, replace=None):
    if replace == None:
        return [p for p in plist if is_valid(p)]
    else:
        return [p if is_valid(p) else replace for p in plist]


def generate_sections(offset_table, line_order):
    '''Generate the cross sections in 3D at each station
    from the given lines and organizes the lines into coordinates
    (x, y, z) = (width, height length). Returns each as a list
    contained in a dictionary'''

    logger.debug('Input to generate offsets')
    for line in offset_table:
        logger.debug(line)

    sections = []
    for line in line_order:
        if line in offset_table:
            sections.append(offset_table[line])

    logger.debug('Un-transformed sections')
    logger.debug(sections)

    # Transpose the list of section
    sections = list(map(list, zip(*sections)))

    clean_sections = []
    upper = []
    lower = []
    for s in sections:
        cs = remove_invalid(s)
        clean_sections.append(cs)
        css = sorted(cs, key=lambda x: x[1])
        upper.append(css[0])
        lower.append(css[-1])

    # Project the top and bottom of profile as their own lines
    upper = [(0.0, p[1], p[2]) for p in upper]
    lower = [(0.0, p[1], p[2]) for p in lower]

    logger.debug('Transformed clean_section')
    for s in clean_sections:
        logger.debug(s)

    logger.debug('upper and lower lines')
    logger.debug(upper)
    logger.debug(lower)
    
    return clean_sections, upper, lower


def try_float(st):
    try:
        x = float(st)
        return x
    except ValueError:
        return st


def lineOrder(table):
    s = set()
    s_add = s.add
    order = [r[1] for r in table if not (r[1] in s or s_add(r[1]))]

    return order


def parse_csv_offsets(filename):
    ''' parse the csv expected offset table fields '''

    with open(filename, 'r') as csvfile:
        raw_table = list(csv.reader(csvfile, delimiter=',', quotechar='"'))

    logger.debug('original table:')
    for i, row in enumerate(raw_table):
        logger.debug('row {0}: {1}'.format(i, row))

    # Remove comments lines
    offset_table = [r for r in raw_table if not r[0].startswith('#')]

    # force rows to lower case
    for i, row in enumerate(offset_table):
        offset_table[i] = [str.lower(x) for x in row]

    # convert any numeric cells to floats
    for i, row in enumerate(offset_table):
        offset_table[i] = [try_float(x) for x in row]

    # replicate 'dittos' in axis column
    current = ''
    for i, row in enumerate(offset_table):
        if row[0] and not current == row[0]:
            current = row[0]
        else:
            row[0] = current
        offset_table[i][0] = current

    # convert feet-inches-eights to decimal inches
    logger.debug('modified table:')
    for i, row in enumerate(offset_table):
        offset_table[i] = [fie_to_di(x) for x in row]
        logger.debug('row {0}: {1}'.format(i, offset_table[i]))

    # create a list of lines names preserving the order they appeared
    line_order = lineOrder(offset_table)
    line_order = line_order[2:]

    logger.debug('extracted the following line names')
    logger.debug(line_order)

    # Break out each set of dimension and recombine as (x, y, z)
    ot_widths = get_all_axis(offset_table, 'width')
    ot_heights = get_all_axis(offset_table, 'height')
    ot_lengths = get_all_axis(offset_table, 'length')

    # Pull out optional section angles
    ot_angles = get_all_axis(offset_table, 'angle')

    # TODO: clean this up, need to skip the '' key
    ot_angles = ot_angles.get('', None)

    ot_combined = {}
    for line_name in ot_widths:
        x = ot_widths[line_name]
        y = ot_heights[line_name]
        z = [float(zs) for zs in ot_lengths['station']]
        line_points = remove_invalid(list(zip(x, y, z)), [])
        ot_combined[line_name] = line_points

    return ot_combined, line_order, ot_angles


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


def rake_angle(offsets, st_index, angle):
    xc_original = offsets['sections'][st_index]

    # Angle is givent in degrees from the baseline
    angle = radians(angle)

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

    # Apply rotation in xz plane around y = y0 to lines
    for name, coords in offsets['lines'].items():
        if coords[st_index]:
            logger.debug("modifying {0} at station {1}".format(name, st_index))
            pt = list(coords[st_index])
            pt = rotate_point(y0, z0, angle, pt)
            coords[st_index] = pt
        else:
            logger.debug("ignoring {0} at station {1}".format(name, st_index))

    return offsets 


def offset_reader(filename):
    ''' read a table of offsets from a csv file and produce a
    dictionary containing the lines and cross sections '''

    offset_data = {}

    # Read the lines from an offset table
    lines, line_order, section_angles = parse_csv_offsets(filename)
    offset_data['lines'] = lines

    # Add a set of cross sections
    sections, upper, lower = generate_sections(lines, line_order)
    offset_data['sections'] = sections
    offset_data['lines']['_upper_cl'] = upper
    offset_data['lines']['_lower_cl'] = lower
    if section_angles:
        offset_data['angle'] = section_angles

    return offset_data


if __name__ == "__main__":
    ''' This is executed when run from the command line '''
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
    logger.debug("arguments" + str(args))

    offset_data = offset_reader(args.filename)

    # Use angles from table if they were given
    # TODO: apply angle at each station
    # TODO: use command line as override
    bindex = 0
    tindex = len(offset_data['sections']) - 1
    if 'angle' in offset_data:
        logger.debug("apply section angles from tables")
        logger.debug(offset_data['angle'])
        ba = offset_data['angle'][bindex]
        ta = offset_data['angle'][tindex]
    else:
        logger.debug("apply section angles from command line")
        ba = float(args.bow_angle)
        ta = float(args.transom_angle)

    # Apply optional rake angles at bow and transom
    offset_data = rake_angle(offset_data, bindex, 90 - ba)
    offset_data = rake_angle(offset_data, tindex, 90 - ta)

    out_filename, _ = os.path.splitext(args.filename)
    out_filename = out_filename + '.json'
    logger.debug('writing json data:\n' + json.dumps(offset_data))
    with open(out_filename, 'w') as opf:
        json.dump(offset_data, opf)
