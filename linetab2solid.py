
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
    # change these to asserst
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
    logging.debug('This message should go to the log file')
    offset_table = pd.read_csv(filename)

    logging.debug('before munging\n' + str(offset_table))

    offset_table = offset_table.drop('name',1)
    offset_table = offset_table.drop('axis',1)
    offset_table = offset_table.set_index('id')
    offset_table = offset_table.applymap(fie_to_di)
    offset_table = offset_table.transpose()

    logging.debug('after munging\n' + str(offset_table))

    return (offset_table)

if __name__ == '__main__':

    offset_table = load_offsets(sys.argv[1])

    section_data = generate_sections(offset_table)
    print (json.dumps(section_data, sort_keys=True))


