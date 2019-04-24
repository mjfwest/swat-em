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
    print('Test if MMK results in the same windingfactor as star of voltage')
    print('double layer winding, tooth-coil')
    Q = 18
    p = 8
    m = 3
    wstep = 1
    layers = 2
    ret = genwdg(Q, 2*p, m, wstep, layers)
    wdglayout = ret['phases']
    data = datamodel()
    data.set_config(get_init_config())
    data.set_machinedata(Q = Q, p = p, m = m)
    data.set_phases(wdglayout)
    data.analyse_wdg()

    nu = data.results['MMK']['nu']
    HA = data.results['MMK']['HA']
    idx = nu.index(p)
    
    Ns = Q*layers/m/2   # number of turns in series
    kw1 = np.abs(HA[idx])*np.pi*p / (3.*Ns)  # winding-factor based on the MMK
        
    idx = data.results['nu_el'].index(1)
    assert np.round(kw1, 4) == np.round(data.results['kw_el'][idx][0], 4) # phase U
    
    #  import matplotlib.pyplot as plt
    #  try: # Interaktives Plotten, wenn Skript aus der ipython Konsole aufgerufen wird
        #  __IPYTHON__
        #  plt.ion()
    #  except NameError:
        #  pass
    #  plt.figure(1)
    #  plt.clf()
    #  plt.grid(True)
    #  plt.stem(range(len(theta)), theta, 'r', markerfmt=' ') #, basefmt=' '
    #  plt.plot(phi, MMK)



def test2():
    print('Test if MMK results in the same windingfactor as star of voltage')
    print('single layer winding, tooth-coil')
    Q = 12
    p = 5
    m = 3
    wstep = 1
    layers = 1
    ret = genwdg(Q, 2*p, m, wstep, layers)
    wdglayout = ret['phases']
    data = datamodel()
    data.set_config(get_init_config())
    data.set_machinedata(Q = Q, p = p, m = m)
    data.set_phases(wdglayout)
    data.analyse_wdg()

    nu = data.results['MMK']['nu']
    HA = data.results['MMK']['HA']
    idx = nu.index(p)
    
    Ns = Q*layers/m/2   # number of turns in series
    kw1 = np.abs(HA[idx])*np.pi*p / (3.*Ns)  # winding-factor based on the MMK
        
    idx = data.results['nu_el'].index(1)
    assert np.round(kw1, 4) == np.round(data.results['kw_el'][idx][0], 4) # phase U
    
    #  import matplotlib.pyplot as plt
    #  try: # Interaktives Plotten, wenn Skript aus der ipython Konsole aufgerufen wird
        #  __IPYTHON__
        #  plt.ion()
    #  except NameError:
        #  pass
    #  plt.figure(1)
    #  plt.clf()
    #  plt.grid(True)
    #  plt.stem(range(len(theta)), theta, 'r', markerfmt=' ') #, basefmt=' '
    #  plt.plot(phi, MMK)


def test3():
    print('Test if MMK results in the same windingfactor as star of voltage')
    print('double layer winding, overlapping')
    Q = 18
    p = 1
    m = 3
    wstep = 6
    layers = 2
    ret = genwdg(Q, 2*p, m, wstep, layers)
    wdglayout = ret['phases']
    data = datamodel()
    data.set_config(get_init_config())
    data.set_machinedata(Q = Q, p = p, m = m)
    data.set_phases(wdglayout)
    data.analyse_wdg()

    nu = data.results['MMK']['nu']
    HA = data.results['MMK']['HA']
    idx = nu.index(p)
    
    Ns = Q*layers/m/2   # number of turns in series
    kw1 = np.abs(HA[idx])*np.pi*p / (3.*Ns)  # winding-factor based on the MMK
        
    idx = data.results['nu_el'].index(1)
    assert np.round(kw1, 4) == np.round(data.results['kw_el'][idx][0], 4) # phase U
    
    #  import matplotlib.pyplot as plt
    #  try: # Interaktives Plotten, wenn Skript aus der ipython Konsole aufgerufen wird
        #  __IPYTHON__
        #  plt.ion()
    #  except NameError:
        #  pass
    #  plt.figure(1)
    #  plt.clf()
    #  plt.grid(True)
    #  plt.stem(range(len(theta)), theta, 'r', markerfmt=' ') #, basefmt=' '
    #  plt.plot(phi, MMK)




if __name__ == '__main__':
    test1()
    test2()
    test3()





