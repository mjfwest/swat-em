# -*- coding: utf-8 -*-
# Test for evaluating the radial force modes

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from swat_em.wdggenerator import genwdg
from swat_em.datamodel import datamodel


def test_num_basic_winding():
    # 2-layer
    data = datamodel()
    data.genwdg(Q = 12, P = 8, m = 3, layers = 2, w = 1)
    bc, _ = data.get_basic_characteristics()
    t = data.calc_num_basic_windings_t()
    assert bc['t'] == t

    data = datamodel()
    data.genwdg(Q = 12, P = 10, m = 3, layers = 2, w = 1)
    bc, _ = data.get_basic_characteristics()
    t = data.calc_num_basic_windings_t()
    assert bc['t'] == t

    data.genwdg(Q = 18, P = 6, m = 3, layers = 2, w = -1)
    bc, _ = data.get_basic_characteristics()
    t = data.calc_num_basic_windings_t()
    assert bc['t'] == t

    data.genwdg(Q = 18, P = 12, m = 3, layers = 2, w = -1)
    bc, _ = data.get_basic_characteristics()
    t = data.calc_num_basic_windings_t()
    assert bc['t'] == t

    data.genwdg(Q = 30, P = 4, m = 3, layers = 2, w = 1)
    bc, _ = data.get_basic_characteristics()
    t = data.calc_num_basic_windings_t()
    assert bc['t'] == t


    # 1-layer
    data = datamodel()
    data.genwdg(Q = 12, P = 10, m = 3, layers = 1, w = 1)
    bc, _ = data.get_basic_characteristics()
    t = data.calc_num_basic_windings_t()
    assert bc['t'] == t


    # this winding-layout may not be correct 
    #  data = datamodel()
    #  data.genwdg(Q = 30, P = 8, m = 3, layers = 1, w = -1)
    #  bc, _ = data.get_basic_characteristics()
    #  t = data.calc_num_basic_windings_t()
    #  assert bc['t'] == t






if __name__ == '__main__':
    test_num_basic_winding()







