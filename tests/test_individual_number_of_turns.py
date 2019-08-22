# -*- coding: utf-8 -*-
# testcase for individual number of turns

# winding data taken from
# AC-Motoren mit verteilter Zahnspulenwicklung
# Gerhard Huth, Jens Krotsch
# e & i Elektrotechnik und Informationstechnik 2019
# https://dx.doi.org/10.1007/s00502-019-0717-9

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from swat_em.datamodel import datamodel
import swat_em.analyse
import numpy as np


def test_doza():
    Q = 12
    p = 1
    m = 3
    wstep = 1
    layers = 2
    U = [[1,2,-11,-12],[5,6,-7,-8]]
    V = [[-3,-4,5,6],[9,10,-11,-12]]
    W = [[-7,-8,9,10],[1,2,-3,-4]]
    S = [U, V, W]

    zs = 1
    dz =  [ zs*0.0,  zs*0.1,  zs*0.2,  zs*0.3]
    kw1 = [ 0.4830,  0.5054,  0.5278,  0.5502]
    kw5 = [-0.1294, -0.0458, -0.0379, -0.1215]
    kw7 = [ 0.1294,  0.0458,  0.0379,  0.1215]

    for k in range(len(dz)):
        za = zs + dz[k]
        zb = zs - dz[k]
        turns = [[[zb,za,za,zb], [za,zb,zb,za]],
                 [[za,zb,zb,za], [za,zb,zb,za]],
                 [[za,zb,zb,za], [za,zb,zb,za]]]

        data = datamodel()
        data.set_machinedata(Q = Q, p = p, m = m)
        data.set_phases(S, turns = turns)
        data.analyse_wdg()
        #  data.save_to_file('doza_{}.wdg'.format(dz[k]))
        bc, txt = data.get_basic_characteristics()
        #  print(bc)

        idx = data.results['nu_el'].index(1)
        assert kw1[k] == np.round(data.results['kw_el'][idx][0], 4) # phase U
        assert kw1[k] == np.round(data.results['kw_el'][idx][1], 4) # phase V
        assert kw1[k] == np.round(data.results['kw_el'][idx][2], 4) # phase W
        idx = data.results['nu_el'].index(5)
        assert kw5[k] == np.round(data.results['kw_el'][idx][0], 4) # phase U
        assert kw5[k] == np.round(data.results['kw_el'][idx][1], 4) # phase V
        assert kw5[k] == np.round(data.results['kw_el'][idx][2], 4) # phase W
        idx = data.results['nu_el'].index(7)
        assert kw7[k] == np.round(data.results['kw_el'][idx][0], 4) # phase U
        assert kw7[k] == np.round(data.results['kw_el'][idx][1], 4) # phase V
        assert kw7[k] == np.round(data.results['kw_el'][idx][2], 4) # phase W


if __name__ == '__main__':
    test_doza()


