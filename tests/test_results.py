# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from swat_em.datamodel import datamodel


def test_is_symmetric():
    wdg = datamodel()
    wdg.genwdg(Q=12, P=2, m=3, w=5, layers=2)
    assert wdg.get_is_symmetric() == True


def test_fundamental_winding_factor():
    wdg = datamodel()
    wdg.genwdg(Q=12, P=2, m=3, w=5, layers=2)
    wf = wdg.get_fundamental_windingfactor()
    wf_expected = [0.933013, 0.933013, 0.933013]
    np.testing.assert_allclose(wf, wf_expected, rtol=1e-3, atol=0)


def test_num_series_turns():
    wdg = datamodel()
    wdg.genwdg(Q=12, P=2, m=3, w=5, layers=2)
    assert wdg.get_num_series_turns() == 4


def test_radial_force_modes():
    wdg = datamodel()
    wdg.genwdg(Q=12, P=2, m=3, w=5, layers=2)
    assert wdg.get_radial_force_modes() == [2, 4, 6]


def test_periodicity():
    wdg = datamodel()
    wdg.genwdg(Q=12, P=2, m=3, w=5, layers=2)
    assert wdg.get_periodicity_t() == 1


def test_parallel_connections():
    wdg = datamodel()
    wdg.genwdg(Q=12, P=2, m=3, w=5, layers=2)
    assert wdg.get_parallel_connections() == [1, 2]


def test_lcmQP():
    wdg = datamodel()
    wdg.genwdg(Q=12, P=2, m=3, w=5, layers=2)
    assert wdg.get_lcmQP() == 12


if __name__ == '__main__':
    test_is_symmetric()
    test_fundamental_winding_factor()
    test_num_series_turns()
    test_radial_force_modes()
    test_periodicity()
    test_parallel_connections()
    test_lcmQP()
