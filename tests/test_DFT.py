# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import swat_em.analyse
import numpy as np
import pdb


def test_DFT():
    print('Test Harmonic Analysis')
    x = np.linspace(0, 2*np.pi, 11)
    y = 10*np.cos(x) + 3*np.cos(3*x)

    HA = np.abs(swat_em.analyse.DFT(y[:-1]))

    assert 10 == np.round(HA[1], 5)
    assert 3 == np.round(HA[3], 5)





if __name__ == '__main__':
    test_DFT()

