
import numpy as np
import pandas as pd
import sys


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


if __name__ == '__main__':
    # TODO: Make a function
    lt = pd.read_csv(sys.argv[1])
    # TODO: Use logger over prints
    print("before munging")
    print (lt)
    lt = lt.drop('name',1)
    lt = lt.drop('axis',1)
    lt = lt.set_index('id')
    lt = lt.applymap(fie_to_di)
    lt = lt.transpose()
    print("after munging")
    print (lt)

    # Generate the cross sections in 3-space 
    # at each station from the given lines
    # TODO: Make it another function
    bottom = []
    chine = []
    gunwale = []
    for index, r in lt.iterrows():
        # Add width, height and station to each 'line' as points (x,y,z)
        chine.append([r.cw,r.ch,r.st])
        bottom.append([r.bw,r.bh,r.st])
        gunwale.append([r.gw,r.gh,r.st])
    
        # Add the points along with a center line to form the cross sections
        section = [[0,r.gh,r.st], [0,r.bh,r.st], [r.bw,r.bh,r.st], [r.cw,r.ch,r.st], [r.gw,r.gh,r.st]]
        print ('        section{0}={1};'.format(index,str(section)))

    print('        bottom={0}'.format(str(bottom)))
    print('        chine={0}'.format(str(chine)))
    print('        gunwale={0}'.format(str(gunwale)))

