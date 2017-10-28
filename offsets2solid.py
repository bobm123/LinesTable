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
from math import isnan

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
    #bottom = []
    #chine = []
    #gunwale = []
    line_order = ['coaming', 'gunwale', 'sheer', 'chine', 'bottom', 'skeg']
    for index, r in lt.iterrows():
        # Add width, height and station to each 'line' as points (x,y,z)
        #chine.append([r.cw,r.ch,r.st])
        #bottom.append([r.bw,r.bh,r.st])
        #gunwale.append([r.gw,r.gh,r.st])
    
        # Add points along each line to form the cross sections
        #s = [[0,r.gh,r.st],     # center at gunwale
        #     [0,r.bh,r.st],     # center at bottom
        #     [r.bw,r.bh,r.st],  # bottom
        #     [r.cw,r.ch,r.st],  # chine
        #     [r.gw,r.gh,r.st]]  # gunwale
        xc = []
        for line in line_order:
            if line in lt:
                xc.append(r[line])

        # Remove any points with NaN in them
        xc = [p for p in xc if valid_coordinate(p)]

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
            line_points = [p for p in line_points if valid_coordinate(p)]
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


def valid_coordinate(point):
    return all(isinstance(w, float) and not isnan(w) for w in point)


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


def main(args):
    offset_table = load_offsets(args.filename)

    offset_data = generate_sections(offset_table)

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



