# -*- coding: utf-8 -*-
# 01_basics.py - Use winding generator

from swat_em import datamodel


# Generate a simple overlapping winding
data = datamodel()      # generate a datamodel for the winding
Q = 6                   # number of slots
P = 2                   # number of pole pairs

# generate winding automatically
data.genwdg(Q = Q, P = P, m = 3, layers = 1)
print(data)             # print infos for the winding


# Generate a simple tooth-coil winding
# Therefore we have to define the winding stepwidth = 1 and
# a lower number of slots
data = datamodel()      # generate a datamodel for the winding
Q = 3                   # number of slots
P = 2                   # number of pole pairs
w = 1                   # step width for the coil in slots

# generate winding automatically
data.genwdg(Q = Q, P = P, m = 3, layers = 2, w = w) 
print(data)             # print infos for the winding



# A more complex winding (overlapping full pitch winding with coil shortening)
data = datamodel()
Q = 12
P = 2
w = 5     # without shortening w would be 6 for this winding
data.genwdg(Q = Q, P = P, m = 3, layers = 2, w = w) 
print(data)


