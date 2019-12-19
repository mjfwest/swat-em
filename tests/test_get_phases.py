# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from swat_em.datamodel import datamodel
import numpy as np



def test_get_layers():
    data = datamodel()
    data.genwdg(Q = 12, P = 10, m = 3, w = 1, layers = 2)
    data.analyse_wdg()
    #  bc, txt = data.get_basic_characteristics()
    #  print(bc)

    l, ls, lcol = data.get_layers()
    #  print(l)
    #  print(ls)
    #  print(lcol)
    assert list(l[0,:]) == [1,2,-2,-3,3,1,-1,-2,2,3,-3,-1] # first layer
    assert list(l[1,:]) == [1,-1,-2,2,3,-3,-1,1,2,-2,-3,3] # second layer

if __name__ == '__main__':
    test_get_layers()






