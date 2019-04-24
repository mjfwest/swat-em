# -*- coding: utf-8 -*-

# Functions for creating windings

import fractions
#  from collections import deque
import math
import numpy as np


def is_even(val):
    '''
    Returns True if absolute value is even
    '''
    return True if abs(val) % 2 is 0 else False


def genwdg(Q, P, m, w, layers):
    """
    Generates a winding layout.

    Parameters
    ----------
    Q :      integer
             number of slots
    P :      integer
             number of poles
    m :      integer
             number of phases
    w :      integer
             winding step (1 for tooth coils)
    layers : integer
             number of coil sides per slot      
             
    Returns
    -------
    return : list
             winding layout (right and left layers) for every phase
    """  
    #  q = fractions.Fraction(Q/(m*P)).limit_denominator(100)
    #  n = q.denominator
    #  z = q.numerator
    
    #  wdglayout = None
    #  if q >= 1:    # overlapping winding
        #  if layers == 1:
            #  wdglayout = overlapping_fractional_slot_slayer(Q, P, m)
        #  else:
            #  wdglayout = overlapping_fractional_slot_dlayer(Q, P, m, w)
    #  else:         # tooth coil winding
        #  if layers == 1:
            #  wdglayout = toothcoil_slayer(Q, P, m)
        #  else:
            #  wdglayout = toothcoil_dlayer(Q, P, m)
    #  if not wdglayout:
        #  print('No winding found')
    
    ret = winding_from_star_of_slot(Q, P, m, w, layers)
        
    return ret




'''


def toothcoil_dlayer(Q, P, m):
    """
    Generates winding layout for double layer tooth coil winding 

    Parameters
    ----------
    Q :      integer
             number of slots
    P :      integer
             number of poles
    m :      integer
             number of phases
             
    Returns
    -------
    return : list
             winding layout for every phase
    """ 
    q = fractions.Fraction(Q/(m*P)).limit_denominator(100)
    n = q.denominator
    z = q.numerator
    cpph = int(Q / m)    # coils per phase
    
    phases = {}
    sign = 1
    i = 1
    for k in range(int(cpph/z)): # for every smallest periodic part of the winding
        for km in range(m):
            if km not in phases.keys():
                phases[km] = [[],[]]
            for k in range(z):
                phases[km][0].append(i*sign)
                i += 1
                phases[km][1].append(-i*sign)
                sign *= -1
            sign *= -1

    # The algorithm starts with a half slot: 1, 2, 2, 3, 3 ... Q+1
    # So the last slot is Q+1 and have to be reduced to slot 1
    for key, value in phases.items():
        for i, k in enumerate(value[0]):
            if k > Q:
                phases[key][0][i] = 1
            elif k < -Q:
                phases[key][0][i] = -1
        for i, k in enumerate(value[1]):
            if k > Q:
                phases[key][1][i] = 1
            elif k < -Q:
                phases[key][1][i] = -1
        
    phases_list = [value for key, value in phases.items()]
    return phases_list


def toothcoil_slayer(Q, P, m):
    """
    Generates winding layout for single layer tooth coil winding 

    Parameters
    ----------
    Q :      integer
             number of slots
    P :      integer
             number of poles
    m :      integer
             number of phases
             
    Returns
    -------
    return : list
             winding layout for every phase
    """  
    q = fractions.Fraction(Q/(m*P)).limit_denominator(100)
    n = q.denominator
    z = q.numerator
    cpph = int(Q / m / 2)    # coils per phase
    
    phases = {}
    sign = 1
    i = 1
    if z%2 == 0: # z is even
        for k in range(int(cpph/z*2)): # for every smallest periodic part of the winding
            for km in range(m):
                if km not in phases.keys():
                    phases[km] = []
                for k in range(int(z/2)):
                    phases[km].append(i*sign)
                    i += 1
                    phases[km].append(-i*sign)
                    i += 1
                sign *= -1
                
    else: # z is odd
        toggle = 1
        for k in range(int(cpph/z*2)): # for every smallest periodic part of the winding
            for km in range(m):
                if km not in phases.keys():
                    phases[km] = []
                for k in range(int((z+toggle)/2)):
                    phases[km].append(i*sign)
                    i += 1
                    phases[km].append(-i*sign)
                    i += 1
                sign *= -1                    
                toggle *= -1

    phases_list = [[value] for key, value in phases.items()]
    return phases_list
'''


def overlapping_fractional_slot_slayer(Q, P, m):
    from collections import deque
    p = P/2
    q = fractions.Fraction(Q/(m*2*p)).limit_denominator(100)
    g = 0  # number of full slots
    while q > 1:
        q -= 1
        g += 1
    
    z2 = q.numerator
    n = q.denominator
    
    # build sequence of coil sides (half of the coil side pairs of the coils)
    cgroups = []    
    for k in range(n):
        if k < z2:
            cgroups.append(g+1)
        if k < (n-z2):
            cgroups.append(g)
    cgroups *= m
    
    # build sequnce of coil sides for each phase (complete pair)
    cgroups_per_phase = [[] for k in range(m) ]
    i = 0
    for g in cgroups:        
        cgroups_per_phase[i].append(g)
        cgroups_per_phase[i].append(-g)
        i += 1
        if i >= m:
            i = 0
    
    if m == 3: # change phase sequence for generating the winding layout
        cgroups_per_phase[1], cgroups_per_phase[2] = cgroups_per_phase[2], cgroups_per_phase[1]
    
    for i in range(m):
        if i%2 is not 0:
            l = deque(cgroups_per_phase[i])
            l.rotate(1)
            cgroups_per_phase[i] = list(l)
    
    # print(cgroups_per_phase)
    # print('z2', z2)
    # print('n', n)
    # print(cgroups)
    
    phases = [[] for k in range(m) ]
    i = 1
    while i < Q:
        for cs in zip(*cgroups_per_phase):
            for km in range(len(cs)):
                for s in range(abs(cs[km])):
                    if cs[km] > 0:
                        phases[abs(km)].append(-i)
                    else:
                        phases[abs(km)].append(i)
                    i += 1
    # print('phases', phases)

    if m == 3: # change phase sequence again
        phases[1], phases[2] = phases[2], phases[1]
    
    for k in range(len(phases)):
        phases[k] = [phases[k]]
    return phases

'''
# Noch zu testen!!!
def overlapping_fractional_slot_dlayer(Q, P, m, w):
    p = P/2
    q = fractions.Fraction(Q/(m*2*p)).limit_denominator(100)
    g = 0  # number of full slots
    while q > g:
        q -= 1
        g += 1    
    z2 = q.numerator
    n = q.denominator
    
    # build sequence of coil sides (half of the coil side pairs of the coils)
    cgroups = []    
    for k in range(n):
        if k < z2:
            cgroups.append(g+1)
        if k < (n-z2):
            cgroups.append(g)
    cgroups *= m
    
    # build sequnce of coil sides for each phase (complete pair)
    cgroups_per_phase = [[] for k in range(m) ]
    i = 0
    for g in cgroups:        
        cgroups_per_phase[i].append(g)
        cgroups_per_phase[i].append(-g)
        i += 1
        if i >= m:
            i = 0
    
    if m == 3: # change phase sequence for generating the winding layout
        cgroups_per_phase[1], cgroups_per_phase[2] = cgroups_per_phase[2], cgroups_per_phase[1]
    
    for i in range(m):
        if i%2 is not 0:
            l = deque(cgroups_per_phase[i])
            l.rotate(1)
            cgroups_per_phase[i] = list(l)    

    phases = [[[], []] for k in range(m) ]
    i = 1
    while i < Q:
        for cs in zip(*cgroups_per_phase):
            for km in range(len(cs)):
                for s in range(abs(cs[km])):
                    if cs[km] > 0:
                        phases[abs(km)][0].append(-i)
                    else:
                        phases[abs(km)][0].append(i)
                    i += 1
    # print('phases', phases)
    # print('w', w)

    if m == 3: # change phase sequence again
        phases[1], phases[2] = phases[2], phases[1]
    
    for km in range(m):
        for ks in range(len(phases[km][0])):
            tmp = phases[km][0][ks]
            tmp2 = abs(tmp) + w
            if tmp2 < 1:
                tmp2 += Q
            if tmp2 > Q:
                tmp2 -= Q            
            if tmp > 0:    # change polarity (opposite coils side)
                tmp2 *= -1
                        
            phases[km][1].append(tmp2)
    
    # print('phases', phases)
    
    
    
    
    
    
    
    return phases

'''


def winding_from_star_of_slot(Q, P, m, w=-1, layers=2):
    #  if layers == 1:
        #  if w == -1:
            #  w = Q // P
            #  if w <= 0:
                #  w = 1
    #  elif layers == 2:
        #  if w == -1:
            #  w = Q // P
            #  if w <= 0:
                #  w = 1
    if w == -1:
        w = Q // P
        if w <= 0:
            w = 1
    # single layer is only feasable if winding step is odd
    # reduce windings step if it is even
    # if layers == 1:
        # if w > 1 and is_even(w):
            # w -= 1
    # print('w', w)
    p = P//2
    
    error = ''
    valid = True
    
    t = math.gcd(Q, p)
    # Test if there are enough slots for the winding
    if layers == 1:
        test1 = fractions.Fraction(Q / (2*m)).limit_denominator(100)
        if test1.denominator is not 1:
            valid = False
            error += 'For single layer winding Q/(2*m) must be an integer\n'
    elif layers == 2:
        test1 = fractions.Fraction(Q / m).limit_denominator(100)
        if test1.denominator is not 1:
            valid = False
            error += 'For double layer winding Q/m must be an integer'
        

    test2 = fractions.Fraction(Q / (m*t)).limit_denominator(100)
    if test2.denominator is not 1:
        valid = False
        error += 'winding not feasible'

    phasors = []
    for k in range(Q):
        a = 2*np.pi*p/Q * k
        a += np.pi/m/4         # shift by half sector range instead of shifting
        a -= 2*np.pi*p/Q/100   # add a small shift because a phasor could match
                               # a sector border exactly
        
        while a > 2*np.pi:     # angle between 0...2pi
            a -= 2*np.pi
        phasors.append(a)

    phases = [[[],[]] for k in range(m)]
    for km in range(m):                   # for every phase
        r = np.pi/m                       # range for sector
        if is_even(m):                    # shifting m=2 (and maybe m=4, 6,...) 
            mp = 1                        # with special treatment
        else:
            mp = 2
        r1 = [mp*km*r, mp*km*r+r]         # sector for positive coils sides
        r2 = [r1[0]+np.pi, r1[1]+np.pi ]  # sector for negative coils sides

        for k in range(len(r1)):          # sector between 0..2pi
            while r1[k] > 2*np.pi:
                r1[k] -= 2*np.pi    
        for k in range(len(r2)):
            while r2[k] > 2*np.pi:
                r2[k] -= 2*np.pi
        
        for i, p in enumerate(phasors):
            # print(i+1, p, r1, r2)
            if p > r1[0] and p <= r1[1]:       # phasor is in positive sector
                phases[km][0].append(i+1)     # slot belongs to the phase
                c = i+1+w
                while c > Q:
                    c -= Q
                phases[km][1].append(-c)       # add the second layer
            if p > r2[0] and p <= r2[1]:       # phasor is in negative sector
                phases[km][0].append(-i-1)            
                c = i+1+w
                while c > Q:
                    c -= Q
                phases[km][1].append(c)


    # remove second layer. Attention: It is important to fill the second
    # layer with the algorithm above, even if single layer is to generate,
    # because there are special cases, where the single layer winding have
    # to be generated from the double layer winding!
    if layers == 1:    # only 
        if not is_even(w):
            for km in range(m):
                a = phases[km]
                a2 = [[], []]
                for k in range(len(a[0])):
                    #  print(a[0][k], a[1][k])
                    if not is_even(a[0][k]):    # use only the odd slots
                        a2[0].append(a[0][k])
                        a2[0].append(a[1][k])   # from second layer to first layer
                phases[km] = a2
        else:
            # use fallback function for w = even!
            q = fractions.Fraction(Q/(m*P)).limit_denominator(100)
            if q.denominator == 1:
                for km in range(m):
                    phases[km][1] = []
            else:
                #  print('single layer winding not suitable', Q, P)
                phases = overlapping_fractional_slot_slayer(Q, P, m)
                w = Q/P

            
    ret = {'phases': phases, 'wstep': w, 'valid': valid, 'error': error }
    return ret
