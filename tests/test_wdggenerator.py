# -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

#  from swat.wdggenerator import genwdg, overlapping_fractional_slot_slayer, overlapping_fractional_slot_dlayer
from swat_em.wdggenerator import genwdg
from swat_em.datamodel import datamodel

#  import swat_em.analyse
import numpy as np
import pdb


def test1():
    print("Test double layer toothcoilwinding")
    Q = 18
    p = 8
    m = 3
    wstep = 1
    layers = 2
    #  U = [[1, -2, 3, 10, -11, 12], [-2, 3, -4, -11, 12, -13]]
    #  V = [[4, -5, 6, 13, -14, 15], [-5, 6, -7, -14, 15, -16]]
    #  W = [[7, -8, 9, 16, -17, 18], [-8, 9, -10, -17, 18, -1]]
    U = [[1, 8, -9, 10, 17, -18], [-2, -9, 10, -11, -18, 1]]
    V = [[2, -3, 4, 11, -12, 13], [-3, 4, -5, -12, 13, -14]]
    W = [[5, -6, 7, 14, -15, 16], [-6, 7, -8, -15, 16, -17]]
    kw1 = 0.9452
    kw5 = -0.1398
    kw7 = -0.0607
    ret = genwdg(Q, 2 * p, m, wstep, layers)
    wdglayout = ret["phases"]
    #  print(wdglayout)
    assert [U, V, W] == wdglayout

    data = datamodel()
    #  data.set_config(get_init_config())
    data.set_machinedata(Q=Q, p=p, m=m)
    data.set_phases(wdglayout)
    data.analyse_wdg()

    idx = data.results["nu_el"].index(1)
    assert kw1 == np.round(data.results["kw_el"][idx][0], 4)  # phase U
    assert kw1 == np.round(data.results["kw_el"][idx][1], 4)  # phase V
    assert kw1 == np.round(data.results["kw_el"][idx][2], 4)  # phase W
    idx = data.results["nu_el"].index(5)
    assert kw5 == np.round(data.results["kw_el"][idx][0], 4)  # phase U
    assert kw5 == np.round(data.results["kw_el"][idx][1], 4)  # phase V
    assert kw5 == np.round(data.results["kw_el"][idx][2], 4)  # phase W
    idx = data.results["nu_el"].index(7)
    assert kw7 == np.round(data.results["kw_el"][idx][0], 4)  # phase U
    assert kw7 == np.round(data.results["kw_el"][idx][1], 4)  # phase V
    assert kw7 == np.round(data.results["kw_el"][idx][2], 4)  # phase W

    bc, txt = data.get_basic_characteristics()
    #  print(bc)


def test2():
    print("Test single layer toothcoilwinding")
    Q = 18
    p = 8
    m = 3
    wstep = 1
    layers = 1
    #  U = [[1,-2,3,-4,-11,12]]
    #  V = [[-5,6,13,-14,15,-16]]
    #  W = [[7,-8,9,-10,-17,18]]
    U = [[1, -2, -9, 10, 17, -18], []]
    V = [[-3, 4, 11, -12, 13, -14], []]
    W = [[5, -6, 7, -8, -15, 16], []]

    kw1 = 0.9452
    kw5 = -0.1398
    kw7 = -0.0607
    ret = genwdg(Q, 2 * p, m, wstep, layers)  # 12/10
    wdglayout = ret["phases"]

    #  print(wdglayout)
    assert [U, V, W] == wdglayout

    data = datamodel()
    #  data.set_config(get_init_config())
    data.set_machinedata(Q=Q, p=p, m=m)
    data.set_phases(wdglayout)
    data.analyse_wdg()

    idx = data.results["nu_el"].index(1)
    assert kw1 == np.round(data.results["kw_el"][idx][0], 4)  # phase U
    assert kw1 == np.round(data.results["kw_el"][idx][1], 4)  # phase V
    assert kw1 == np.round(data.results["kw_el"][idx][2], 4)  # phase W
    idx = data.results["nu_el"].index(5)
    assert kw5 == np.round(data.results["kw_el"][idx][0], 4)  # phase U
    assert kw5 == np.round(data.results["kw_el"][idx][1], 4)  # phase V
    assert kw5 == np.round(data.results["kw_el"][idx][2], 4)  # phase W
    idx = data.results["nu_el"].index(7)
    assert kw7 == np.round(data.results["kw_el"][idx][0], 4)  # phase U
    assert kw7 == np.round(data.results["kw_el"][idx][1], 4)  # phase V
    assert kw7 == np.round(data.results["kw_el"][idx][2], 4)  # phase W


def test3():
    print("Test single layer toothcoilwinding")
    Q = 12
    p = 4
    m = 3
    wstep = 1
    layers = 1
    U = [[1, -2, 7, -8], []]
    V = [[5, -6, 11, -12], []]
    W = [[3, -4, 9, -10], []]
    kw1 = 0.866
    kw5 = -0.866
    kw7 = 0.866
    ret = genwdg(Q, 2 * p, m, wstep, layers)  # 12/10
    wdglayout = ret["phases"]
    #  print(wdglayout)
    assert [U, V, W] == wdglayout

    data = datamodel()
    data.set_machinedata(Q=Q, p=p, m=m)
    data.set_phases(wdglayout)
    data.analyse_wdg()

    idx = data.results["nu_el"].index(1)
    assert kw1 == np.round(data.results["kw_el"][idx][0], 4)  # phase U
    assert kw1 == np.round(data.results["kw_el"][idx][1], 4)  # phase V
    assert kw1 == np.round(data.results["kw_el"][idx][2], 4)  # phase W
    idx = data.results["nu_el"].index(5)
    assert kw5 == np.round(data.results["kw_el"][idx][0], 4)  # phase U
    assert kw5 == np.round(data.results["kw_el"][idx][1], 4)  # phase V
    assert kw5 == np.round(data.results["kw_el"][idx][2], 4)  # phase W
    idx = data.results["nu_el"].index(7)
    assert kw7 == np.round(data.results["kw_el"][idx][0], 4)  # phase U
    assert kw7 == np.round(data.results["kw_el"][idx][1], 4)  # phase V
    assert kw7 == np.round(data.results["kw_el"][idx][2], 4)  # phase W


def test4():
    print("Test single layer toothcoilwinding")
    Q = 12
    p = 5
    m = 3
    wstep = 1
    layers = 1
    U = [[1, -2, -7, 8], []]
    V = [[-3, 4, 9, -10], []]
    W = [[5, -6, -11, 12], []]
    kw1 = 0.9659
    kw5 = -0.2588
    kw7 = 0.2588
    ret = genwdg(Q, 2 * p, m, wstep, layers)  # 12/10
    wdglayout = ret["phases"]
    #  print(wdglayout)
    assert [U, V, W] == wdglayout

    data = datamodel()
    data.set_machinedata(Q=Q, p=p, m=m)
    data.set_phases(wdglayout)
    data.analyse_wdg()

    idx = data.results["nu_el"].index(1)
    assert kw1 == np.round(data.results["kw_el"][idx][0], 4)  # phase U
    assert kw1 == np.round(data.results["kw_el"][idx][1], 4)  # phase V
    assert kw1 == np.round(data.results["kw_el"][idx][2], 4)  # phase W
    idx = data.results["nu_el"].index(5)
    assert kw5 == np.round(data.results["kw_el"][idx][0], 4)  # phase U
    assert kw5 == np.round(data.results["kw_el"][idx][1], 4)  # phase V
    assert kw5 == np.round(data.results["kw_el"][idx][2], 4)  # phase W
    idx = data.results["nu_el"].index(7)
    assert kw7 == np.round(data.results["kw_el"][idx][0], 4)  # phase U
    assert kw7 == np.round(data.results["kw_el"][idx][1], 4)  # phase V
    assert kw7 == np.round(data.results["kw_el"][idx][2], 4)  # phase W


def test5():
    print("Test single layer toothcoilwinding")
    Q = 24
    p = 11
    m = 3
    wstep = 1
    layers = 1
    U = [[1, -2, -11, 12, -13, 14, 23, -24], []]
    V = [[-3, 4, -5, 6, 15, -16, 17, -18], []]
    W = [[7, -8, 9, -10, -19, 20, -21, 22], []]
    kw1 = 0.9577
    kw5 = -0.2053
    kw7 = -0.1576
    ret = genwdg(Q, 2 * p, m, wstep, layers)  # 12/10
    wdglayout = ret["phases"]
    #  print(wdglayout)
    assert [U, V, W] == wdglayout

    data = datamodel()
    data.set_machinedata(Q=Q, p=p, m=m)
    data.set_phases(wdglayout)
    data.analyse_wdg()

    idx = data.results["nu_el"].index(1)
    assert kw1 == np.round(data.results["kw_el"][idx][0], 4)  # phase U
    assert kw1 == np.round(data.results["kw_el"][idx][1], 4)  # phase V
    assert kw1 == np.round(data.results["kw_el"][idx][2], 4)  # phase W
    idx = data.results["nu_el"].index(5)
    assert kw5 == np.round(data.results["kw_el"][idx][0], 4)  # phase U
    assert kw5 == np.round(data.results["kw_el"][idx][1], 4)  # phase V
    assert kw5 == np.round(data.results["kw_el"][idx][2], 4)  # phase W
    idx = data.results["nu_el"].index(7)
    assert kw7 == np.round(data.results["kw_el"][idx][0], 4)  # phase U
    assert kw7 == np.round(data.results["kw_el"][idx][1], 4)  # phase V
    assert kw7 == np.round(data.results["kw_el"][idx][2], 4)  # phase W


def test6():
    print("Test single layer full pitch winding")
    Q = 24
    p = 2
    m = 3
    wstep = -1
    layers = 1
    U = [[1, 2, -7, -8, 13, 14, -19, -20], []]
    V = [[5, 6, -11, -12, 17, 18, -23, -24], []]
    W = [[-3, -4, 9, 10, -15, -16, 21, 22], []]
    kw1 = 0.9659
    kw5 = -0.2588
    kw7 = 0.2588
    #  wdglayout = genwdg(Q, 2*p, m, wstep, layers) # 12/10
    ret = genwdg(Q, 2 * p, m, wstep, layers)
    wdglayout = ret["phases"]
    #  print(wdglayout)
    #  pdb.set_trace()
    assert [U, V, W] == wdglayout

    data = datamodel()
    data.set_machinedata(Q=Q, p=p, m=m)
    data.set_phases(wdglayout)
    data.analyse_wdg()

    idx = data.results["nu_el"].index(1)
    assert kw1 == np.round(data.results["kw_el"][idx][0], 4)  # phase U
    assert kw1 == np.round(data.results["kw_el"][idx][1], 4)  # phase V
    assert kw1 == np.round(data.results["kw_el"][idx][2], 4)  # phase W
    idx = data.results["nu_el"].index(5)
    assert kw5 == np.round(data.results["kw_el"][idx][0], 4)  # phase U
    assert kw5 == np.round(data.results["kw_el"][idx][1], 4)  # phase V
    assert kw5 == np.round(data.results["kw_el"][idx][2], 4)  # phase W
    idx = data.results["nu_el"].index(7)
    assert kw7 == np.round(data.results["kw_el"][idx][0], 4)  # phase U
    assert kw7 == np.round(data.results["kw_el"][idx][1], 4)  # phase V
    assert kw7 == np.round(data.results["kw_el"][idx][2], 4)  # phase W


def test7():
    print("Test two layer full pitch winding")
    Q = 24
    p = 2
    m = 3
    wstep = 5
    layers = 2
    U = [[1, 2, -7, -8, 13, 14, -19, -20], [-6, -7, 12, 13, -18, -19, 24, 1]]
    V = [[5, 6, -11, -12, 17, 18, -23, -24], [-10, -11, 16, 17, -22, -23, 4, 5]]
    W = [[-3, -4, 9, 10, -15, -16, 21, 22], [8, 9, -14, -15, 20, 21, -2, -3]]
    kw1 = 0.9330
    kw5 = -0.0670
    kw7 = 0.0670
    ret = genwdg(Q, 2 * p, m, wstep, layers)  # 12/10
    wdglayout = ret["phases"]
    #  wdglayout = overlapping_fractional_slot_dlayer(Q, 2*p, m, wstep)
    #  print(wdglayout)
    #  pdb.set_trace()
    assert [U, V, W] == wdglayout

    data = datamodel()
    data.set_machinedata(Q=Q, p=p, m=m)
    data.set_phases(wdglayout)
    data.analyse_wdg()

    idx = data.results["nu_el"].index(1)
    assert kw1 == np.round(data.results["kw_el"][idx][0], 4)  # phase U
    assert kw1 == np.round(data.results["kw_el"][idx][1], 4)  # phase V
    assert kw1 == np.round(data.results["kw_el"][idx][2], 4)  # phase W
    idx = data.results["nu_el"].index(5)
    assert kw5 == np.round(data.results["kw_el"][idx][0], 4)  # phase U
    assert kw5 == np.round(data.results["kw_el"][idx][1], 4)  # phase V
    assert kw5 == np.round(data.results["kw_el"][idx][2], 4)  # phase W
    idx = data.results["nu_el"].index(7)
    assert kw7 == np.round(data.results["kw_el"][idx][0], 4)  # phase U
    assert kw7 == np.round(data.results["kw_el"][idx][1], 4)  # phase V
    assert kw7 == np.round(data.results["kw_el"][idx][2], 4)  # phase W


def test_8():
    print("test empty slots detection")
    Q = 12
    P = 8
    m = 3
    w = 1
    layers = 2

    wdg1 = datamodel()
    wdg1.genwdg(Q=Q, P=P, m=m, w=w, layers=layers, empty_slots=0)

    wdg2 = datamodel()
    wdg2.genwdg(
        Q=Q, P=P, m=m, w=w, layers=layers, empty_slots=-1
    )  # test for right detection
    assert wdg1.get_fundamental_windingfactor() == wdg2.get_fundamental_windingfactor()


def test_combinations_table():
    """
    Test a big table of different slot/pole combinations. The winding
    factors are taken from following paper:

    Libert, F. & Soulard, Juliette. (2004). Investigation on Pole-Slot Combinations for Permanent-Magnet Machines with Concentrated Windings. 

    https://www.researchgate.net/publication/237458473_Investigation_on_Pole-Slot_Combinations_for_Permanent-Magnet_Machines_with_Concentrated_Windings
    """
    print("Test a big table of different slot/pole combinations")

    wf = {}
    wf[6] = {
        4: 0.866,
        8: 0.866,
        10: 0.5,
        14: 0.5,
        16: 0.866,
        20: 0.866,
        22: 0.5,
        26: 0.5,
        28: 0.866,
        32: 0.866,
        34: 0.5,
        38: 0.5,
        40: 0.866,
    }
    wf[9] = {
        4: 0.616,
        6: 0.866,
        8: 0.945,
        10: 0.945,
        12: 0.866,
        14: 0.617,
        16: 0.328,
        20: 0.328,
        22: 0.617,
        24: 0.866,
        26: 0.945,
        28: 0.945,
        30: 0.866,
        32: 0.617,
        34: 0.328,
        38: 0.328,
        40: 0.617,
        42: 0.866,
    }
    wf[12] = {
        8: 0.866,
        10: 0.933,
        14: 0.933,
        16: 0.866,
        32: 0.866,
        34: 0.933,
        38: 0.933,
        40: 0.866,
    }
    wf[15] = {
        8: 0.621,
        10: 0.866,
        14: 0.951,
        16: 0.951,
        22: 0.621,
        38: 0.621,
        40: 0.866,
    }
    wf[18] = {
        10: 0.647,
        12: 0.866,
        14: 0.902,
        16: 0.945,
    }
    wf[21] = {14: 0.866, 16: 0.890, 20: 0.953, 22: 0.953, 26: 0.890, 28: 0.866}
    wf[24] = {
        14: 0.760,
        16: 0.866,
        20: 0.933,
        22: 0.950,
        26: 0.95,
        28: 0.933,
        32: 0.866,
        34: 0.760,
    }
    wf[27] = {
        18: 0.866,
        20: 0.877,
        22: 0.915,
        24: 0.945,
        26: 0.954,
        28: 0.954,
        30: 0.945,
        32: 0.915,
        34: 0.877,
        36: 0.866,
    }
    wf[30] = {
        20: 0.866,
        22: 0.874,
        26: 0.936,
        28: 0.951,
        32: 0.951,
        34: 0.936,
        38: 0.874,
        40: 0.866,
    }
    wf[33] = {
        22: 0.866,
        26: 0.903,
        28: 0.928,
        32: 0.954,
        34: 0.954,
        38: 0.928,
        40: 0.903,
    }
    wf[36] = {
        24: 0.866,
        26: 0.867,
        28: 0.902,
        30: 0.933,
        32: 0.945,
        34: 0.953,
        38: 0.953,
        40: 0.945,
        42: 0.933,
    }
    wf[39] = {26: 0.866, 28: 0.863, 32: 0.918, 34: 0.936, 38: 0.954, 40: 0.954}
    wf[42] = {28: 0.866, 32: 0.890, 34: 0.913, 38: 0.945, 40: 0.953}

    wf[45] = {
        42: 0.951,
        44: 0.955,
        46: 0.955,
        48: 0.951,
        50: 0.945,
        52: 0.927,
        56: 0.886,
        58: 0.859,
        60: 0.866,
    }
    wf[48] = {
        44: 0.950,
        46: 0.954,
        50: 0.954,
        52: 0.950,
        56: 0.933,
        58: 0.905,
        62: 0.857,
        64: 0.866,
    }
    wf[51] = {
        44: 0.933,
        46: 0.944,
        50: 0.955,
        52: 0.955,
        56: 0.944,
        58: 0.933,
        62: 0.901,
        64: 0.880,
        68: 0.866,
    }
    wf[54] = {
        42: 0.902,
        44: 0.915,
        46: 0.930,
        48: 0.945,
        50: 0.949,
        52: 0.954,
        56: 0.954,
        58: 0.949,
        60: 0.945,
        62: 0.930,
        64: 0.915,
        66: 0.902,
        68: 0.877,
        70: 0.854,
        72: 0.866,
    }
    wf[57] = {
        44: 0.932,
        46: 0.912,
        50: 0.937,
        52: 0.946,
        56: 0.955,
        58: 0.955,
        62: 0.946,
        64: 0.937,
        68: 0.912,
        70: 0.932,
        74: 0.852,
        76: 0.866,
    }
    wf[60] = {
        44: 0.874,
        46: 0.892,
        50: 0.933,
        52: 0.936,
        56: 0.951,
        58: 0.954,
        62: 0.954,
        64: 0.951,
        68: 0.936,
        70: 0.933,
        74: 0.892,
        76: 0.874,
        80: 0.866,
    }
    wf[63] = {
        42: 0.866,
        44: 0.850,
        46: 0.871,
        48: 0.890,
        50: 0.905,
        52: 0.919,
        56: 0.945,
        58: 0.948,
        60: 0.953,
        62: 0.955,
        64: 0.955,
        66: 0.953,
        68: 0.948,
        70: 0.945,
        74: 0.919,
        76: 0.905,
        78: 0.890,
        80: 0.871,
    }
    wf[66] = {
        44: 0.866,
        46: 0.849,
        50: 0.887,
        52: 0.903,
        56: 0.928,
        58: 0.938,
        62: 0.951,
        64: 0.954,
        68: 0.954,
        70: 0.951,
        74: 0.938,
        76: 0.928,
        80: 0.903,
    }
    wf[69] = {
        46: 0.866,
        50: 0.867,
        52: 0.884,
        56: 0.914,
        58: 0.925,
        62: 0.943,
        64: 0.949,
        68: 0.955,
        70: 0.955,
        74: 0.949,
        76: 0.943,
        80: 0.925,
    }
    wf[72] = {
        48: 0.866,
        50: 0.847,
        52: 0.867,
        56: 0.902,
        58: 0.911,
        60: 0.933,
        62: 0.933,
        64: 0.945,
        66: 0.950,
        68: 0.953,
        70: 0.954,
        74: 0.954,
        76: 0.953,
        78: 0.950,
        80: 0.945,
    }
    wf[75] = {
        50: 0.866,
        52: 0.846,
        56: 0.880,
        58: 0.895,
        62: 0.920,
        64: 0.930,
        68: 0.945,
        70: 0.951,
        74: 0.955,
        76: 0.955,
        80: 0.951,
    }
    wf[78] = {
        52: 0.866,
        56: 0.863,
        58: 0.879,
        62: 0.906,
        64: 0.918,
        68: 0.936,
        70: 0.943,
        74: 0.952,
        76: 0.954,
        80: 0.954,
    }
    wf[81] = {
        54: 0.866,
        56: 0.845,
        58: 0.860,
        60: 0.877,
        62: 0.890,
        64: 0.904,
        66: 0.915,
        68: 0.925,
        70: 0.933,
        72: 0.945,
        74: 0.946,
        76: 0.951,
        78: 0.954,
        80: 0.955,
    }
    wf[84] = {
        56: 0.866,
        58: 0.845,
        62: 0.876,
        64: 0.890,
        68: 0.913,
        70: 0.933,
        74: 0.939,
        76: 0.945,
        80: 0.953,
    }
    wf[87] = {
        58: 0.866,
        62: 0.859,
        64: 0.874,
        68: 0.899,
        70: 0.910,
        74: 0.929,
        76: 0.936,
        80: 0.947,
    }
    wf[90] = {
        60: 0.866,
        62: 0.843,
        64: 0.859,
        66: 0.874,
        68: 0.886,
        70: 0.902,
        74: 0.918,
        76: 0.927,
        78: 0.936,
        80: 0.945,
    }

    # Some of the windingfactors doesn't match;
    # these cases are excluded to prevent asserts
    exclude = [
        (15, 8),  # SWAT-EM finds a winding with a higher windingfactor
        (15, 22),  # SWAT-EM finds a winding with a higher windingfactor
        (15, 38),  # SWAT-EM finds a winding with a higher windingfactor
        (18, 10),  # SWAT-EM finds a winding with a higher windingfactor
        (57, 44),  # high windingfactor from the paper can't be reached here
        (57, 70),  # high windingfactor from the paper can't be reached here
        (81, 58),
    ]  # Wrong last digit in the paper??

    for slot, poles in wf.items():
        for P, wf in poles.items():
            if (slot, P) not in exclude:
                wdg = datamodel()
                wdg.genwdg(Q=slot, P=P, m=3, layers=2, w=1)
                wf2 = wdg.get_fundamental_windingfactor()[0]
                wf2 = np.round(np.abs(wf2), 3)
                if not np.allclose(wf, wf2, atol=0.001):
                    print(slot, P, wf, wf2)
                assert np.allclose(wf, wf2, atol=0.001)


def test_single_phase():
    print("Test single phase winding")
    wdg = datamodel()
    wdg.genwdg(Q=4, P=4, m=1, layers=2, w=1)
    assert wdg.get_fundamental_windingfactor()[0] == 1.0


"""
# Test is maybe not correct!!!
def test8():
    print('Test overlapping fractional slot winding with single layer')
    # TODO: Referenzdaten ergänzen
    Q = 33
    p = 2
    m = 3
    #  wstep = 1
    layers = 1
    U = [[1, 2, 3, -9, -10, -11, 17, 18, 19, -26, -27], []]
    V = [[6, 7, 8, -15, -16, 23, 24, 25, -31, -32, -33], []]
    W = [[-4, -5, 12, 13, 14, -20, -21, -22, 28, 29, 30], []]
    kw1 = 0.954208
    kw5 = 0.187366
    kw7 = 0.131332
    ret = genwdg(Q, 2*p, m, None, layers) # 12/10
    wdglayout = ret['phases']
    print(wdglayout)
    assert [U, V, W] == wdglayout

    data = datamodel()
    data.set_machinedata(Q = Q, p = p, m = m)
    data.set_phases(wdglayout)
    data.analyse_wdg()
    #  pdb.set_trace()
    idx = data.results['nu_el'].index(1)
    assert kw1 == np.round(data.results['kw_el'][idx][0], 4) # phase U
    assert kw1 == np.round(data.results['kw_el'][idx][1], 4) # phase V
    assert kw1 == np.round(data.results['kw_el'][idx][2], 4) # phase W
    idx = data.results['nu_el'].index(5)
    assert kw5 == np.round(data.results['kw_el'][idx][0], 4) # phase U
    assert kw5 == np.round(data.results['kw_el'][idx][1], 4) # phase V
    assert kw5 == np.round(data.results['kw_el'][idx][2], 4) # phase W
    idx = data.results['nu_el'].index(7)
    assert kw7 == np.round(data.results['kw_el'][idx][0], 4) # phase U
    assert kw7 == np.round(data.results['kw_el'][idx][1], 4) # phase V
    assert kw7 == np.round(data.results['kw_el'][idx][2], 4) # phase W
"""


if __name__ == "__main__":
    test1()
    test2()
    test3()
    test4()
    test5()
    test6()
    test7()
    test_8()
    test_combinations_table()
    test_single_phase()
