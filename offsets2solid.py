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

logging.basicConfig(filename='offsets2solid.log',level=logging.DEBUG)


def fie_to_di(d):
    '''Convets dimenstion in feet-inches-eigths to decimal inches'''

    if isinstance(d, str):
        fie = d.split(',')
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
    bottom = []
    chine = []
    gunwale = []
    for index, r in lt.iterrows():
        # Add width, height and station to each 'line' as points (x,y,z)
        chine.append([r.cw,r.ch,r.st])
        bottom.append([r.bw,r.bh,r.st])
        gunwale.append([r.gw,r.gh,r.st])
    
        # Add points along each line to form the cross sections
        s = [[0,r.gh,r.st],     # center at gunwale
             [0,r.bh,r.st],     # center at bottom
             [r.bw,r.bh,r.st],  # bottom
             [r.cw,r.ch,r.st],  # chine
             [r.gw,r.gh,r.st]]  # gunwale
        sections.append(s)

    # Put it all in a dictionary
    offset_data = {
        'sections': sections,
        'bottom': bottom,
        'chine' : chine,
        'gunwale' : gunwale}

    return offset_data


def load_offsets(filename):
    offset_table = pd.read_csv(filename)

    logging.debug('before munging\n' + str(offset_table))

    offset_table = offset_table.drop('name',1)
    offset_table = offset_table.drop('axis',1)
    offset_table = offset_table.set_index('id')
    offset_table = offset_table.applymap(fie_to_di)
    offset_table = offset_table.transpose()

    logging.debug('after munging\n' + str(offset_table))

    return (offset_table)


def main(args):
    offset_table = load_offsets(args.filename)

    section_data = generate_sections(offset_table)
    print (json.dumps(section_data, sort_keys=True))


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



