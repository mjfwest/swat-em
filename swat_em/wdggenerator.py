# -*- coding: utf-8 -*-

# Functions for creating windings

import fractions
#  from collections import deque
import math
import numpy as np
from swat_em import analyse


def is_even(val):
    '''
    Returns True if absolute value is even
    '''
    return True if abs(val) % 2 == 0 else False


def genwdg(Q, P, m, w, layers, empty_slots = 0):
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
    if empty_slots <= 0:
        ret = winding_from_star_of_slot(Q, P, m, w, layers)
        if not ret['valid'] and empty_slots != 0:
            ret = winding_from_general_equation(Q, P, m, w, layers, empty_slots)
    else:
        ret = winding_from_general_equation(Q, P, m, w, layers, empty_slots)
    return ret


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
        #  print('g', g)
        i += 1
        if i >= m:
            i = 0
    
    if m == 3: # change phase sequence for generating the winding layout
        cgroups_per_phase[1], cgroups_per_phase[2] = cgroups_per_phase[2], cgroups_per_phase[1]
    
    for i in range(m):
        if i%2 != 0:
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
    #  print('phases', phases)
    #  print('cgroups_per_phase', cgroups_per_phase)

    if m == 3: # change phase sequence again
        phases[1], phases[2] = phases[2], phases[1]
    
    for k in range(len(phases)):
        phases[k] = [phases[k], []]
        
    # windingsteps for the fractional slot winding
    w = [0]*len(cgroups_per_phase[0])
    #  for i, cg in enumerate(cgroups_per_phase):
        #  for k in range(len(cg)):
            #  w[k] += abs(cg[k])
            #  print('w[i]', w[i])
    
    cg2 = list(map(list, zip(*cgroups_per_phase))) # transpose
    w = []
    for cg in cg2:
        cg = [abs(k) for k in cg]
        w.append(sum(cg))
    #  print('w', w)
    w = w[:len(w)//2]
    
    
    #  print('cg2', cg2)
    #  print('w', w)
    return phases, w




def winding_from_star_of_slot(Q, P, m, w=-1, layers=2):
    '''
    Based on:
    N. Bianchi and M. Dai Pre, "Use of the star of slots in designing fractional-slot single-layer synchronous motors," in IEE Proceedings - Electric Power Applications, vol. 153, no. 3, pp. 459-466, 1 May 2006.
    doi: 10.1049/ip-epa:20050284
    keywords: {synchronous motors;machine windings;torque;losses;fault tolerance;harmonics;coils;fractional-slot winding;single-layer synchronous motor;end-winding loss reduction;torque ripple;mutual coupling reduction;fault-tolerant application;one side coil;slot star;graphical representation;analytical formulation;harmonic content},
    URL: http://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=1629527&isnumber=34185
    '''
    if hasattr(w, '__iter__'):
        w = -1   # fractional slot has list of w's
    
    if w == -1:
        w = Q // P
        if w <= 0:
            w = 1

    p = P//2
    
    error = ''
    valid = True
    
    t = math.gcd(Q, p)
    # Test if there are enough slots for the winding
    if layers == 1:
        test1 = fractions.Fraction(Q / (2*m)).limit_denominator(100)
        if test1.denominator != 1:
            valid = False
            error += 'For single layer winding Q/(2*m) must be an integer\n'
    elif layers == 2:
        test1 = fractions.Fraction(Q / m).limit_denominator(100)
        if test1.denominator != 1:
            valid = False
            error += 'For double layer winding Q/m must be an integer'
        

    test2 = fractions.Fraction(Q / (m*t)).limit_denominator(100)
    if test2.denominator != 1:
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
                phases, w = overlapping_fractional_slot_slayer(Q, P, m)
                #  w = Q/P

            
    ret = {'phases': phases, 'wstep': w, 'valid': valid, 'error': error, 'info': '', 'Qes': 0}
    return ret


def winding_from_general_equation(Q, P, m, w=-1, layers=2, n_es = 0):
    '''
    Based on:
    Caruso, Massimo & Di Tommaso, Antonino & Marignetti, Fabrizio & Miceli, Rosario & Galluzzo, Giuseppe. (2018). A General Mathematical Formulation for Winding Layout Arrangement of Electrical Machines. Energies. 11. 446. 10.3390/en11020446. 
    '''
    error = ''
    info = ''
    valid = True
    S = [[[]]*m]
    if layers == 1 and w == 1:
        info += 'Coil pitch w = 1 could not be applied'
    
    N = Q
    p = P // 2
    n_lay = layers
    if layers == 2 and w == -1:
        w = Q // P
        if w <= 0:
            w = 1
    
    if m != 1 and Q % m != 0:
        valid = False
        error += 'Number of slots must be a multiple of the number of phases'
    
    if valid:
        if n_es >= 0:
            n_wc = n_lay*(N-n_es)/(2*m)
        else:
            n_wc = n_lay*(N- 0  )/(2*m)
        t = math.gcd(N, p)

        # symmetric winding?
        if m%2 == 0:
            g = n_lay*N / (2*m*t)
        else:
            g = N / (2*m*t)
        #  if int(g) != g:
            #  if int(n_wc) != n_wc:
                #  valid = False
                #  error += 'winding not symmetric'

    if valid:
        # dead coil winding (empty slots)
        if n_es == -1:
            n_es = int(N - 2*m*int(n_wc) / n_lay)

        if n_es != 0:
            info += 'attention: dead coil winding'
        #  print('empty_slots:', n_es)
        q = fractions.Fraction( (N-n_es) / (2*p*m) ).limit_denominator(1000)
        a = int(q)
        z = q.numerator - a


    if valid:
        # create winding distribution table
        n_c = int(N / m)
        #  print('Q', Q, 'p', p, 'n_c', n_c)
        WDT = np.zeros(m*n_c, dtype=int)
        i=1
        while i <= N:
            ind = np.mod(p*(i-1)+1, N)
            if ind == 0:
                ind = N
            while WDT[ind-1] != 0:
                ind = ind+1
            WDT[ind-1] = i
            i = i+1
            ind = ind+1

        WDT = WDT.reshape(m, n_c)


        if m%2 == 0:
            shift = int(m/2-1)
        else:
            shift = int( (m-1)/2 )

    # for some bar windings
    #  if fractions.Fraction(n_wc).limit_denominator(1000).denominator == 2:
        #  shift = n_wc + 1 # this  
        #  shift = n_wc - 1 # or this is possible
    
    if valid:
        #  print('Q', Q, 'p', p, 'n_es', n_es, 'n_c', n_c)
        # non-ruduced and normal systems
        if m%2 != 0:
            a = WDT[:,:int(n_c/2)]
            b = WDT[:,int(n_c/2):] * (-1)
            b = np.roll(b, -shift, axis=0)
            WDT2 = np.append(a,b,axis=1)
        else:
            dx = int(n_c/2)
            dy = int(m/2)
            a = WDT[:dy,:dx]
            b = WDT[:dy,dx:] * (-1)
            c = WDT[dy:,:dx] * (-1)
            d = WDT[dy:,dx:]
            
            
            try:
                left = np.append(a, b, axis=0)
                right = np.append(c, d, axis=0)
                WDT2 = np.append(left, right, axis=1)
            except:
                # Error
                WDT2 = WDT
                valid = False
                error += 'winding not feasable'
                
        if n_es > 0:
            WDT2 = WDT2[:,:-int(n_es/m)]

        S = []
        for k in range(np.shape(WDT2)[0]):
            s = WDT2[k,:]
            idx = np.argsort(np.abs(s))
            s = s[idx]
            S.append([s.tolist(),[]])

        if n_lay == 2:
            for k in range(len(S)):
                for s in S[k][0]:
                    sign = 1 if s > 0 else -1
                    s = abs(s) + w
                    while s > N:
                        s -= N
                    while s < 1:
                        s += N
                    S[k][1].append(sign*(-1)*s)
        
        if n_lay == 1:
            w = fractions.Fraction(N / (2*p))
    
    if valid:
        v, x = analyse.check_number_of_coilsides(S)
        if not v:
            valid = False
        error += x
        

    ret = {'phases': S, 'wstep': w, 'valid': valid, 'error': error, 'info': info, 'Qes': n_es}
    return ret
