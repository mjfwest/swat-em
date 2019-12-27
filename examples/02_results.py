# -*- coding: utf-8 -*-
# 02_results.py - Analyze the winding

from swat_em import datamodel


# A more complex winding (overlapping full pitch winding with coil shortening)
data = datamodel()
Q = 12
P = 2
m = 3
l = 2
data.genwdg(Q = 12, P = 2, m = 3, layers = 1) 

print('fundamental winding factor: ', data.get_fundamental_windingfactor())
print('winding step              : ', data.get_windingstep())


# Get the winding layout. For each phase there is a list of the 1st and 
# the 2nd layer. In this example there is only 1 layer, so the second
# list is empty. An entry of the lists define the slot number in which
# is a coil-side of the phase is located. A negative number means, that 
# the winding direction is reversed in the slot.
print('winding layout:', data.get_phases())


# The winding factor depends on the harmonic number. There are two 
# possible interpretations for the harmonic number: The 'electrical'
# harmonic numbers the 'mechanical' ordinal numbers multiplyed with
# number of pole pairs 'p'. Use the 'mechanical' winding factor if you
# want du determine the possible number of poles your winding can drive
# and use the electrical winding factor if you know your number of pole
# pairs and if you want to analyze the harmonic content of the winding
# for example.
# Attention: The winding factor is calculated for each phase seperately.
nu, kw = data.get_windingfactor_el()
print('nu kw')
for k in range(len(nu)):
    print(nu[k], kw[k])


# the datamodel() object stores the data in dictionaries. The user 
# have direct access:
print('Data for the machine: ', data.machinedata.keys())

# ... and all results:
print('Data for the machine: ', data.results.keys())
