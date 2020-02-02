# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from swat_em.datamodel import datamodel


def test_dead_coil_winding():
    print('test dead coil winding')
    wdg = datamodel()
    wdg.genwdg(Q = 27, P = 6, m = 3, layers = 1, empty_slots = -1)
    #  print('valid:', wdg.generator_info['valid'])
    #  print('error:', wdg.generator_info['error'])
    #  print('info:', wdg.generator_info['info'])

    S = wdg.get_phases()
    U = [1,2,-6,10,-14,-15,19,-23]
    V = [4,5,-9,13,-17,-18,22,-26]
    W = [-3,7,8,-11,-12,16,-20,25]

    assert S[0][0] == U
    assert S[1][0] == V
    assert S[2][0] == W


if __name__ == '__main__':
    test_dead_coil_winding()


