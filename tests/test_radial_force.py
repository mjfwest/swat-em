# -*- coding: utf-8 -*-
# Test for evaluating the radial force modes

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from swat_em.wdggenerator import genwdg
from swat_em.datamodel import datamodel


def test_radial_force_modes1():
    data = datamodel()
    data.genwdg(Q = 9, P = 6, m = 3, layers = 2, w = 1)
    print('Q:', data.get_num_slots(), '2p:', 2*data.get_num_polepairs())
    modes = data.get_radial_force_modes(num_modes = 4)
    print('radial force modes:', modes)
    assert modes == [3, 6, 9, 12]


def test_radial_force_modes2():
    data = datamodel()
    data.genwdg(Q = 9, P = 8, m = 3, layers = 2, w = 1)
    print('Q:', data.get_num_slots(), '2p:', 2*data.get_num_polepairs())
    modes = data.get_radial_force_modes(num_modes = 4)
    print('radial force modes:', modes)
    assert modes == [1, 2, 3, 4]


def test_radial_force_modes3():
    data = datamodel()
    data.genwdg(Q = 12, P = 10, m = 3, layers = 2, w = 1)
    print('Q:', data.get_num_slots(), '2p:', 2*data.get_num_polepairs())
    modes = data.get_radial_force_modes(num_modes = 4)
    print('radial force modes:', modes)
    assert modes == [2, 4, 6, 8]


def test_radial_force_modes4():
    data = datamodel()
    data.genwdg(Q = 24, P = 22, m = 3, layers = 2, w = 1)
    print('Q:', data.get_num_slots(), '2p:', 2*data.get_num_polepairs())
    modes = data.get_radial_force_modes(num_modes = 4)
    print('radial force modes:', modes)
    assert modes == [2, 4, 6, 8]


if __name__ == '__main__':
    test_radial_force_modes1()
    test_radial_force_modes2()
    test_radial_force_modes3()
    test_radial_force_modes4()






