# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from swat_em.datamodel import datamodel
from swat_em.config import config

# The double linked leakage depends on the infinity fourier series
# of the mmf. The number of harmonic numbers depends on the number of
# points in the time domain. For the tests these number of points
# are set to a fixed value:
config['num_MMF_points'] = 3601


def test1():
    print('tooth coil winding 12/10')
    wdg = datamodel()
    wdg.genwdg(Q=12, P=10, m=3, w=1, layers=2)
    sigma_d = wdg.get_double_linked_leakage()
    #  print('sigma_d:', sigma_d)
    np.testing.assert_allclose(sigma_d, 0.968, rtol=1e-3, atol=0)


def test2():
    print('tooth coil winding 12/14')
    wdg = datamodel()
    wdg.genwdg(Q=12, P=14, m=3, w=1, layers=2)
    sigma_d = wdg.get_double_linked_leakage()
    #  print('sigma_d:', sigma_d)
    np.testing.assert_allclose(sigma_d, 2.8579, rtol=1e-3, atol=0)


def test3():
    print('single layer winding with constant number of turns')
    wdg = datamodel()
    wdg.genwdg(Q=6, P=2, m=3, w=-1, layers=1)
    sigma_d = wdg.get_double_linked_leakage()
    #  print('sigma_d:', sigma_d)
    np.testing.assert_allclose(sigma_d, 0.09662, rtol=1e-3, atol=0)


def test4():
    print('single layer winding with constant number of turns')
    wdg = datamodel()
    turns = 1
    S     = [[1, -4], [-2, 5], [3, -6]]
    turns = [[1,  1], [ 1, 1], [1,  1]]
    wdg.set_machinedata(Q = 6, p = 1, m = 3)
    wdg.set_phases(S, turns = turns)
    wdg.analyse_wdg()
    sigma_d = wdg.get_double_linked_leakage()
    #  print('sigma_d:', sigma_d)
    np.testing.assert_allclose(sigma_d, 0.09662, rtol=1e-3, atol=0)


def test5():
    print('single layer winding with constant number of turns')
    wdg = datamodel()
    turns = 100
    S     = [[1, -4], [-2, 5], [3, -6]]
    turns = [[1,  1], [ 1, 1], [1,  1]]
    wdg.set_machinedata(Q = 6, p = 1, m = 3)
    wdg.set_phases(S, turns = turns)
    wdg.analyse_wdg()
    sigma_d = wdg.get_double_linked_leakage()
    #  print('sigma_d:', sigma_d)
    np.testing.assert_allclose(sigma_d, 0.09662, rtol=1e-3, atol=0)


def test6():
    print('single layer winding with variable number of turns')
    wdg = datamodel()
    turns = [[[10,  10],[]], [[ 10, 10],[]], [[10,  10],[]]]
    S     = [[1, -4], [-2, 5], [3, -6]]
    turns = [[1,  1], [ 1, 1], [1,  1]]
    wdg.set_machinedata(Q = 6, p = 1, m = 3)
    wdg.set_phases(S, turns = turns)
    wdg.analyse_wdg()
    sigma_d = wdg.get_double_linked_leakage()
    #  print('sigma_d:', sigma_d)
    np.testing.assert_allclose(sigma_d, 0.09662, rtol=1e-3, atol=0)


if __name__ == '__main__':
    test1()
    test2()
    test3()
    test4()
    test5()
    test6()

