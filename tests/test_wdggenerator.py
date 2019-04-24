# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#  from swat.wdggenerator import genwdg, overlapping_fractional_slot_slayer, overlapping_fractional_slot_dlayer
from swat_em.wdggenerator import genwdg
from swat_em.datamodel import datamodel
from swat_em.config import get_init_config
import swat_em.analyse
import numpy as np
import pdb

def test1():
    print('Test double layer toothcoilwinding')
    Q = 18
    p = 8
    m = 3
    wstep = 1
    layers = 2
    #  U = [[1, -2, 3, 10, -11, 12], [-2, 3, -4, -11, 12, -13]]
    #  V = [[4, -5, 6, 13, -14, 15], [-5, 6, -7, -14, 15, -16]]
    #  W = [[7, -8, 9, 16, -17, 18], [-8, 9, -10, -17, 18, -1]]
    U = [[1,  8, -9, 10, 17, -18], [-2, -9, 10, -11, -18, 1]]
    V = [[2, -3, 4, 11, -12, 13], [-3, 4, -5, -12, 13, -14]]
    W = [[5, -6, 7, 14, -15, 16], [-6, 7, -8, -15, 16, -17]]
    kw1 = 0.9452		
    kw5 = -0.1398		
    kw7 = -0.0607
    ret = genwdg(Q, 2*p, m, wstep, layers)
    wdglayout = ret['phases']
    print(wdglayout)
    assert [U, V, W] == wdglayout
    

    data = datamodel()
    data.set_config(get_init_config())
    data.set_machinedata(Q = Q, p = p, m = m)
    data.set_phases(wdglayout)
    data.analyse_wdg()

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
    
    bc = swat_em.analyse.get_basic_characteristics(Q, m, 2*p, wdglayout)
    print(bc)


def test2():
    print('Test single layer toothcoilwinding')
    Q = 18
    p = 8
    m = 3
    wstep = 1
    layers = 1
    #  U = [[1,-2,3,-4,-11,12]]
    #  V = [[-5,6,13,-14,15,-16]]
    #  W = [[7,-8,9,-10,-17,18]]
    U = [[1, -2, -9, 10, 17, -18],[]]
    V = [[-3, 4, 11, -12, 13, -14],[]]
    W = [[5, -6, 7, -8, -15, 16],[]]
   
    kw1 = 0.9452		
    kw5 = -0.1398		
    kw7 = -0.0607
    ret = genwdg(Q, 2*p, m, wstep, layers) # 12/10
    wdglayout = ret['phases']
    
    print(wdglayout)
    assert [U, V, W] == wdglayout
    
    data = datamodel()
    data.set_config(get_init_config())
    data.set_machinedata(Q = Q, p = p, m = m)
    data.set_phases(wdglayout)
    data.analyse_wdg()

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
    

def test3():
    print('Test single layer toothcoilwinding')
    Q = 12
    p = 4
    m = 3
    wstep = 1
    layers = 1
    U = [[1,-2,7,-8],[]]
    V = [[5,-6,11,-12],[]]
    W = [[3,-4,9,-10],[]]
    kw1 = 0.866
    kw5 = -0.866
    kw7 = 0.866
    ret = genwdg(Q, 2*p, m, wstep, layers) # 12/10
    wdglayout = ret['phases']
    print(wdglayout)
    assert [U, V, W] == wdglayout

    data = datamodel()
    data.set_config(get_init_config())
    data.set_machinedata(Q = Q, p = p, m = m)
    data.set_phases(wdglayout)
    data.analyse_wdg()

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


def test4():
    print('Test single layer toothcoilwinding')
    Q = 12
    p = 5
    m = 3
    wstep = 1
    layers = 1
    U = [[1,-2,-7,8],[]]
    V = [[-3,4,9,-10],[]]
    W = [[5,-6,-11,12],[]]
    kw1 = 0.9659		
    kw5 = -0.2588
    kw7 = 0.2588
    ret = genwdg(Q, 2*p, m, wstep, layers) # 12/10
    wdglayout = ret['phases']
    print(wdglayout)
    assert [U, V, W] == wdglayout

    data = datamodel()
    data.set_config(get_init_config())
    data.set_machinedata(Q = Q, p = p, m = m)
    data.set_phases(wdglayout)
    data.analyse_wdg()

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


def test5():
    print('Test single layer toothcoilwinding')
    Q = 24
    p = 11
    m = 3
    wstep = 1
    layers = 1
    U = [[1, -2, -11, 12, -13, 14, 23, -24],[]]
    V = [[-3, 4, -5, 6, 15, -16, 17, -18],[]]
    W = [[7, -8, 9, -10, -19, 20, -21, 22],[]]
    kw1 = 0.9577	
    kw5 = -0.2053
    kw7 = -0.1576
    ret = genwdg(Q, 2*p, m, wstep, layers) # 12/10
    wdglayout = ret['phases']
    print(wdglayout)
    assert [U, V, W] == wdglayout

    data = datamodel()
    data.set_config(get_init_config())
    data.set_machinedata(Q = Q, p = p, m = m)
    data.set_phases(wdglayout)
    data.analyse_wdg()

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


def test6():
    print('Test single layer full pitch winding')
    Q = 24
    p = 2
    m = 3
    wstep = -1
    layers = 1
    U = [[1, 2, -7, -8, 13, 14, -19, -20],[]]
    V = [[5, 6, -11, -12, 17, 18, -23, -24],[]]
    W = [[-3, -4, 9, 10, -15, -16, 21, 22],[]]
    kw1 = 0.9659	
    kw5 = -0.2588
    kw7 = 0.2588
    #  wdglayout = genwdg(Q, 2*p, m, wstep, layers) # 12/10
    ret = genwdg(Q, 2*p, m, wstep, layers)
    wdglayout = ret['phases']
    print(wdglayout)
    #  pdb.set_trace()
    assert [U, V, W] == wdglayout

    data = datamodel()
    data.set_config(get_init_config())
    data.set_machinedata(Q = Q, p = p, m = m)
    data.set_phases(wdglayout)
    data.analyse_wdg()

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


def test7():
    print('Test two layer full pitch winding')
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
    ret = genwdg(Q, 2*p, m, wstep, layers) # 12/10
    wdglayout = ret['phases']
    #  wdglayout = overlapping_fractional_slot_dlayer(Q, 2*p, m, wstep)
    print(wdglayout)
    #  pdb.set_trace()
    assert [U, V, W] == wdglayout

    data = datamodel()
    data.set_config(get_init_config())
    data.set_machinedata(Q = Q, p = p, m = m)
    data.set_phases(wdglayout)
    data.analyse_wdg()

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
    data.set_config(get_init_config())
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



if __name__ == '__main__':
    test1()
    test2()
    test3()
    test4()
    test5()
    test6()
    test7()
    #  test8()





