# -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from swat_em.datamodel import datamodel
import numpy as np



def test1():
    print("Test 9-phase winding")
    Q = 45
    p = 5
    m = 9
    wstep = -1
    layers = 2


    kw1 = 0.9848
    kw2 = 0.3420
    kw3 = 0.8660

    wdg = datamodel()
    wdg.genwdg(Q=Q, P = 2*p, m=m, w=wstep, layers=layers)
    np.testing.assert_allclose(kw1, wdg.get_windingfactor_el_by_nu(1)[0], rtol=0.001)
    np.testing.assert_allclose(kw2, wdg.get_windingfactor_el_by_nu(2)[0], rtol=0.001)
    np.testing.assert_allclose(kw3, wdg.get_windingfactor_el_by_nu(3)[0], rtol=0.001)



if __name__ == "__main__":
    test1()
