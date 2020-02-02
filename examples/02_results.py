# -*- coding: utf-8 -*-
# 02_results.py - Analyze the winding

from swat_em import datamodel


# A more complex winding (overlapping full pitch winding with coil shortening)
wdg = datamodel()
wdg.genwdg(Q = 12, P = 2, m = 3, layers = 1) 

print('fundamental winding factor: ', wdg.get_fundamental_windingfactor())
print('winding step              : ', wdg.get_windingstep())


# Get the winding layout. For each phase there is a list of the 1st and 
# the 2nd layer. In this example there is only 1 layer, so the second
# list is empty. An entry of the lists define the slot number in which
# is a coil-side of the phase is located. A negative number means, that 
# the winding direction is reversed in the slot.
print('winding layout:', wdg.get_phases())


# The winding factor depends on the harmonic number. There are two 
# possible interpretations for the harmonic number: The 'electrical'
# harmonic numbers the 'mechanical' ordinal numbers multiplyed with
# number of pole pairs 'p'. Use the 'mechanical' winding factor if you
# want du determine the possible number of poles your winding can drive
# and use the electrical winding factor if you know your number of pole
# pairs and if you want to analyze the harmonic content of the winding
# for example.
# Attention: The winding factor is calculated for each phase seperately.
nu, kw = wdg.get_windingfactor_el()
print('nu kw')
for k in range(len(nu)):
    print(nu[k], kw[k])


# the datamodel() object stores the data in dictionaries. The user 
# have direct access:
print('Data for the machine: ', wdg.machinedata.keys())

# ... and all results:
print('Data for the machine: ', wdg.results.keys())

# Use the get_* methods for the results:
print('\nDETAILLED RESULTS: ')
print('Is winding symmetric:         ', wdg.get_is_symmetric())
print('Fundamental winding factor:   ', wdg.get_fundamental_windingfactor())
print('Number of turns in series:    ', wdg.get_num_series_turns())
print('Excited radial force modes:   ', wdg.get_radial_force_modes())
print('Periodictiy:                  ', wdg.get_periodicity_t())
print('Possible parallel connections:', wdg.get_parallel_connections())
print('Double linked leakage:        ', wdg.get_double_linked_leakage())

