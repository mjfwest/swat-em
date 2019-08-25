# -*- coding: utf-8 -*-
# Test detection of the max. possible parallel connection of a winding
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from swat_em.wdggenerator import genwdg
from swat_em.datamodel import datamodel
import swat_em.analyse
import numpy as np
import pdb


def test_parallel_circuit():
    Q         = [12, 12, 9, 12, 27]
    P         = [10,  8, 8,  2, 18]
    m         = [3,   3, 3,  3,  3]
    wstep     = [1,   1, 1,  6,  1]
    layers    = [2,   2, 2,  1,  2]
    a_desired = [2,   4, 1,  2,  9] 

    print('test for max. number of parallel circuits')
    for k in range(len(Q)):
        print('test with Q = {}, 2p = {}, m = {}, wstep = {}, layers = {}'.format(
           Q[k], P[k], m[k], wstep[k], layers[k]))
        ret = genwdg(Q[k], P[k], m[k], wstep[k], layers[k])

        data = datamodel()
        data.set_machinedata(Q = Q[k], p = P[k]/2, m = m[k])
        data.set_phases(ret['phases'])
        bc, txt = data.get_basic_characteristics()
        assert a_desired[k] == bc['a']



if __name__ == '__main__':
    test_parallel_circuit()




