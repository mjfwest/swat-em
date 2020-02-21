# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from swat_em import datamodel



wdg = datamodel()

#  wdg.genwdg(Q=12, P=10, m=3, w=1, layers=2) # passt
#  wdg.genwdg(Q=12, P=10, m=3, w=1, layers=1) # passt


#  wdg.genwdg(Q=6, P=2, m=3, w=-1, layers=1)
#  wdg.genwdg(Q=12, P=2, m=3, w=-1, layers=1)
#  wdg.genwdg(Q=12, P=2, m=3, w=6, layers=2)
#  wdg.genwdg(Q=12, P=2, m=3, w=5, layers=2)

#  wdg.genwdg(Q=12, P=4, m=3, w=-1, layers=1)

#  wdg.genwdg(Q=9, P=2, m=3, w=-1, layers=2)

wdg.genwdg(Q=18, P=4, m=3, w=-1, layers=1)  # fractional slot

#  plot_overhang(self, filename, res = None, show = False, optimize_overhang = False)
wdg.plot_overhang('overhang.png')



#  S = [[1, 2, -7, -8], [5, 6, -11, -12], [-3, -4, 9, 10]]
#  wdg.set_machinedata(Q=12, p=1, m=3)
#  wdg.set_phases(S)
