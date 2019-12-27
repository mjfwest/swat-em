# -*- coding: utf-8 -*-
# 03_graphics.py - Generating plots of the winding

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from swat_em import datamodel


data = datamodel()
Q = 12
P = 2
m = 3
l = 2
data.genwdg(Q = 12, P = 2, m = 3, layers = 1) 


# The winding layout shows all slots with the corresponding
# coil sides of all phases
data.plot_layout('plot_layout.png')

# The winding factor is analyzes by the slot voltage phasors. 
# The following is the corresponding visualization.
data.plot_star('plot_star.png')

# For the winding factor one have to decide between the mechanical or 
# the electrical winding factor. Attention: For a 2-pole machine
# the electrical and mechanical winding factor is equal.
data.plot_windingfactor('plot_wf.png', mechanical = False)

# The winding generates a current linkage in the slots. The 
# integral of it leads to a magnetic field in the airgap, which 
# is called the 'Magnetomotive force (MMF)'. It's a good indicator
# for the harmonic content of the winding.
# 
# The resultion of the image can be definded
data.plot_MMK('plot_MMK.png', res = [800, 600], phase = 0)
