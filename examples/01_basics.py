# -*- coding: utf-8 -*-
# 01_basics.py - Use winding generator

from swat_em import datamodel


# Generate a simple overlapping winding
wdg = datamodel()       # generate a datamodel for the winding
Q = 6                   # number of slots
P = 2                   # number of pole pairs

# generate winding automatically
wdg.genwdg(Q = Q, P = P, m = 3, layers = 1)
print(wdg)             # print infos for the winding


# Generate a simple tooth-coil winding
# Therefore we have to define the winding stepwidth = 1 and
# a lower number of slots
wdg = datamodel()       # generate a datamodel for the winding
Q = 3                   # number of slots
P = 2                   # number of pole pairs
cs = 1                  # coil span for the coil in slots

# generate winding automatically
wdg.genwdg(Q = Q, P = P, m = 3, layers = 2, coil_span = cs) 
print(wdg)             # print infos for the winding



# A more complex winding (overlapping full pitch winding with coil shortening)
wdg = datamodel()
Q = 12
P = 2
cs = 5     # without shortening cs would be 6 for this winding
wdg.genwdg(Q = Q, P = P, m = 3, layers = 2, coil_span = cs) 
print(wdg)


