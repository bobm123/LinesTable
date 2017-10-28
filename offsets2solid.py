#!/usr/bin/env python3
'''
Generates a set of points defining the cross sections and "lines"
of a boat holl given a table of offsets
'''

__author__ = "Robert Marchese"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import json
import logging
import pandas as pd
import sys
from math import isnan, radians, sin, cos

# Setup Logging
logger = logging.getLogger('offsets')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('offsets2solid.log')
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG) #change to ERROR or WARNING after deplot
log_fmt = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(log_fmt)
ch.setFormatter(log_fmt)
logger.addHandler(fh)
logger.addHandler(ch)


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


def test_fie_conversion():
    # change these to asserts, put in tests
    print (fie_to_di("0,0,0"))
    print (fie_to_di("1,0,0"))
    print (fie_to_di("0,1,0"))
    print (fie_to_di("0,0,1"))
    print (fie_to_di("4,4,4"))


def generate_sections(lt):
    '''Generate the cross sections in 3D at each station 
    from the given lines and organizes the lines into coordinates
    (x, y, z) = (width, height length). Returns each as a list
    contained in a dictionary'''

    sections = []
    line_order = ['coaming', 'gunwale', 'sheer', 'chine', 'bottom', 'skeg']
    for index, r in lt.iterrows():
        xc = []
        for line in line_order:
            if line in lt:
                xc.append(r[line])

        # Remove any points with NaN in them
        xc = remove_invalid(xc)

        # project the first and last points onto CL
        first = [0, xc[0][1], xc[0][2]]
        last = [0, xc[-1][1], xc[-1][2]]
        xc = [first] + xc + [last]

        sections.append(xc)

    # Put the sections and lines in a dictionary
    offset_data = {'sections': sections}
    lines_data = {}
    for line in line_order:
        if line in lt:
            line_points = list(lt[line])
            #print("before " + str(line_points))
            line_points = remove_invalid(line_points, [])
            #print("after " + str(line_points))
            lines_data[line] = line_points
    offset_data['lines'] = lines_data

    return offset_data


def repeat_value (ot, ncol):
    '''replicates missing values from one row to the next'''
    column_n = ot.iloc[:,ncol]
    current = ''
    new_column_n = []
    for row in column_n:
        if row and not row == current:
            current = row
        else:
            row = current
        new_column_n.append(row)

    return new_column_n


def get_all_axis(df, axis):
    ''' get all rows with a specific axis (width, height, length)
    and set 'name' as the index. Return the transpose '''
    df_part = df[df['axis'].str.contains(axis)]
    df_part = df_part.set_index('name')
    df_part = df_part.drop('axis', 1)
    
    return (df_part.transpose())


def is_valid(point):
    return all(isinstance(w, float) and not isnan(w) for w in point)


def remove_invalid(plist, replace=None):
    if replace == None:
        return [p for p in plist if is_valid(p)]
    else:
        return [p if is_valid(p) else [] for p in plist]


def load_offsets(filename):
    ''' load a table of offsets and convert seperate rows into columns
    of points (width, height, length) representing each line '''
    ot = pd.read_csv(filename)
    ot = ot.fillna('')

    logger.debug('before munging\n' + str(ot))

    # Drop any comments
    column_0 = ot.iloc[:,0]
    ot = ot[column_0.str.startswith('#') == False]

    # Repeate axis lables ('width', 'heigh')
    ot.iloc[:,0] = repeat_value(ot, 0)

    # Convert feet-inches-eights to decimal inches
    ot = ot.applymap(fie_to_di)

    # Break out each set of dimension and recombine as (x,y,z)
    ot_widths = get_all_axis(ot, 'width')
    ot_heights = get_all_axis(ot, 'height')
    ot_lengths = get_all_axis(ot, 'length')
    ot_combined = pd.DataFrame(index=ot_widths.index)
    for col in ot_widths:
        x = ot_widths[col]
        y = ot_heights[col]
        z = ot_lengths['station'].astype('float')
        ot_combined[col] = list(zip(x, y, z))

    logger.debug('after munging\n' + str(ot_combined))

    return (ot_combined)


def rotate_point(cy, cz, angle, p):
    ''' rotate by an angle in the yz-plane '''
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


def main(args):
    offset_table = load_offsets(args.filename)

    offset_data = generate_sections(offset_table)

    # Apply optional rake angles at bow and transom
    # TODO: Move this operation to F360 scripts
    bindex = 0
    offset_data = rake_angle(offset_data, bindex, 18)
    tindex = len(offset_data['sections']) - 1
    offset_data = rake_angle(offset_data, tindex, -25)

    logger.debug('writing json data:\n' + json.dumps(offset_data))
    with open('data.json', 'w') as outfile:
        json.dump(offset_data, outfile)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("filename", help="input .csv file (offset table)")

    # Optional argument flag which defaults to False
    #parser.add_argument("-f", "--flag", action="store_true", default=False)

    # Optional argument which requires a parameter (eg. -d test)
    #parser.add_argument("-n", "--name", action="store", dest="name")

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    #parser.add_argument(
    #    "-v",
    #    "--verbose",
    #    action="count",
    #    default=0,
    #    help="Verbosity (-v, -vv, etc)")

    # Specify output of "--version"
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)



