# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pdb

from swat_em import datamodel

def test1():
    print('Test saving and loading of data files inc. results and options')
    data = datamodel()
    data.set_machinedata(Q = 12, p = 5, m = 3)

    U = [[1,8],[-2,-7]]
    V = [[4,9],[-3,-10]]
    W = [[5,12],[-6,-11]]    

    data.set_phases([U, V, W])
    data.analyse_wdg()

    data.save_to_file('savefile.wdg')
    data2 = datamodel()
    data2.load_from_file('savefile.wdg')
    os.remove('savefile.wdg')

    assert data.machinedata == data2.machinedata
    #  assert data.results == data2.results


if __name__ == '__main__':
    test1()

