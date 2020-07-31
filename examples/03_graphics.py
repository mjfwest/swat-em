# -*- coding: utf-8 -*-
# 03_graphics.py - Generating plots of the winding

from swat_em import datamodel


wdg = datamodel()
wdg.genwdg(Q = 12, P = 2, m = 3, layers = 1) 


# The winding layout shows all slots with the corresponding
# coil sides of all phases
wdg.plot_layout('plot_layout.png')

# Visualization of the winding overhang (connection of the coil sides)
wdg.plot_overhang('overhang.png')

# Visualization of the winding layout and overhang (connection of the coil sides)
# in polar coordinates
wdg.plot_polar_layout('layout_polar.png', draw_poles = True)

# The winding factor is analyzes by the slot voltage phasors. 
# The following is the corresponding visualization.
wdg.plot_star('plot_star.png')

# For the winding factor one have to decide between the mechanical or 
# the electrical winding factor. Attention: For a 2-pole machine
# the electrical and mechanical winding factor is equal.
wdg.plot_windingfactor('plot_wf.png', mechanical = False)

# The winding generates a current linkage in the slots. The 
# integral of it leads to a magnetic field in the airgap, which 
# is called the 'Magnetomotive force (MMF)'. It's a good indicator
# for the harmonic content of the winding.
# 
# The resultion of the image can be definded
wdg.plot_MMK('plot_MMK.png', res = [800, 600], phase = 0)

# It's also could be usefull to plot at different phase angles
wdg.plot_MMK('plot_MMK_20deg.png', res = [800, 600], phase = 20)
