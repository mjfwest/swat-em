# -*- coding: utf-8 -*-
'''
Provides functions for analyzing windings
''' 
import numpy as np
import fractions
import math
from collections import Counter


def calc_q(Q, p, m):
    return fractions.Fraction(Q / (m * 2*p)).limit_denominator(100)

def get_basic_characteristics(Q, P, m, S):
    q = fractions.Fraction(Q / (m * P)).limit_denominator(100)
    Ei, kw = calc_star(Q, S, P/2, 1)
    a = wdg_get_periodic([Ei], S)
    if a:
        a = min(a) if len(a) > 0 else 1
    else:
        a = 1
    sym = wdg_is_symmetric([Ei], m)
    t = math.gcd(int(Q), int(P/2))
    lcmQP = int(np.lcm(int(Q), int(P)))
    bc = {'q': q, 'kw1': kw, 'a': a, 'sym': sym, 't': t, 'lcmQP': lcmQP}
    return bc
    

def wdg_get_periodic(Ei, S):
    '''
    Returns the symmetry factor for the winding 

    Parameters
    ----------
    Ei :     list of lists of lists
             voltage vectors for every phase and every slot
             Ei[nu][phase][slot]
             
    Returns
    -------
    return : list
             symmetry factor for each phase. 
             1 if there is no periodicity
             2 if half of the machine is smallest symmetric part and so on...
    ''' 
    if len(Ei) == 0:
        return 1
    if len(Ei[0]) == 0:
        return 1
    
    # This is correct for all tooth coil windings but not for full pitch windings
    Ei = Ei[0] # only for fundamental
    S = [item for sublist in S for item in sublist]  # flatten layers
    periodic = []
    for ei in Ei:
        angles = [np.round(np.angle(k)/np.pi*180, 4) for k in ei]
        c = Counter(angles)
        a = min(c.values()) if len(c.values()) > 0 else 1
        periodic.append( a )
    
    #  Ei = np.array(Ei[0]) # only for fundamental
    #  S = np.array(S)

    # This is correct for full pitch windings but not for tooth-coil windings
    #  Ei = Ei[0] # only for fundamental
    #  periodic = []
    #  for km in range(len(Ei)):
        #  ei = np.array(Ei[km]).flatten()
        #  s = [item for sublist in S[km] for item in sublist]  # flatten layers
        #  s = np.array(s)
        #  angles_pos = np.round(np.angle(ei[s>0])/np.pi*180, 4)
        #  angles_neg = np.round(np.angle(ei[s<0])/np.pi*180, 4)
        #  c_pos = Counter(angles_pos)
        #  c_neg = Counter(angles_neg)
        #  a_pos = min(c_pos.values()) if len(c_pos.values()) > 0 else 1
        #  a_neg = min(c_neg.values()) if len(c_neg.values()) > 0 else 1
        #  periodic.append( min([a_pos, a_neg]) )
    
    
    # T
    #  Ei = Ei[0] # only for fundamental
    #  periodic = []
    #  for ei in Ei:
        #  angles = [np.round(np.angle(k)/np.pi*180, 4) for k in ei]
        #  c = Counter(angles)
        #  a = max(c.values()) if len(c.values()) > 0 else 1
        #  a = a/2
        #  if a<1:
            #  a = 1
        #  a = int(a)
        #  periodic.append( a )
    
    #  Ei = np.array(Ei[0]) # only for fundamental
    #  S = np.array(S)
    
    
    
    return periodic


def wdg_is_symmetric(Ei, m):
    '''
    Test if the winding ist symmetric -> phase shift between every 
    phase is 360°/m. 

    Parameters
    ----------
    Ei :     list of lists of lists
             voltage vectors for every phase and every slot
             Ei[nu][phase][slot]
    m  :     integer
             number of phases     
             
    Returns
    -------
    return : bool
             True if symmetric, False if not

    ''' 
    if len(Ei) == 0:
        return None
    if len(Ei[0]) == 0:
        return None
    ei = Ei[0] # only for fundamental
    angles = [np.angle(np.sum(k))/np.pi*180 for k in ei]
    angles = [np.round(k, 4) for k in angles]
    length = [np.abs(np.sum(k)) for k in ei]
    #  print('angles1', angles)
    if m % 2 == 0: # shift all phasors to >180 for even number of phases
        angles = np.array(angles)
        angles += 360
        angles -= min(angles)
        for k in range(len(angles)):
            if angles[k] < 180:
                angles[k] += 360
        angles = angles.tolist()

    angles.sort()
    #  print('angles2', angles)
    if m%2 == 0:
        target_angle = 360 / (2*m)
    else:
        target_angle = 360 / m
    diff = np.diff(angles)
    sym = True
    #  print('diff', diff)
    # Test for phase angles
    for d in diff:
        if not np.isclose(target_angle, d, rtol=1e-02, atol=1e-02):
            sym = False
    # Test for amplitude
    for k in range(1, len(length)):
        if not np.isclose(length[0], length[k], rtol=1e-02, atol=1e-02):
            sym = False
    return sym


def calc_phaseangle_starvoltage(Ei):
    '''
    Calculates the phaseangle based on the slot voltage vectors. 

    Parameters
    ----------
    Ei :     list of lists of lists
             voltage vectors for every phase and every slot
             Ei[nu][phase][slot]
             
    Returns
    -------
    return phaseangle: list
                       phaseangle for every harmonic number and every
                       phase; phaseangle[nu][phase]
    return seqeunce:   list
                       sequence of the flux wave: 1 or -1
    ''' 
    phaseangle = []
    for knu in Ei:             # for every nu
        phaseangle.append([])
        angle = [np.angle(sum(km))*180/np.pi for km in knu] # for every phase
        for a in angle:
            while a < 0:
                a += 360.0
            phaseangle[-1].append( a ) 

    sequence = []
    for p in phaseangle:
        if p[1] > p[0]:
            sequence.append(1)
        else:
            sequence.append(-1)
    #  if sequence[0] < 0:  # related to the fundamental
        #  sequence = [-k for k in sequence]

    return phaseangle, sequence


def calc_kw(Q, S, p, N_nu, config):
    '''
    Calculates the windingfactor, the slot voltage vectors. The 
    harmonic numbers are generated automatically.

    Parameters
    ----------
    Q :      integer
             number of slots
    S :      list of lists
             winding layout
    p :      integer
             number of pole pairs
    N_nu:    integer
             length of the harmonic number vector
             
    Returns
    -------
    return nu: list
               harmonic numbers with relevant winding factor
    return Ei: list of lists of lists
               voltage vectors for every phase and every slot
               Ei[nu][phase][slot]
    return wf: list of lists
               winding factor for every phase. The sign defines the
               direction of the flux wave
               wf[nu][phase]
    '''
    #  S = [item for sublist in S for item in sublist]  # flatten layers
    nu = [] # order
    wf = [] # winding factor
    Ei = [] # slot voltage vectors
    k = 1
    while len(wf) < N_nu:
        a, b = calc_star(Q, S, p, k)
        if np.all(np.abs(b) > config['kw_min']):
            nu.append(k)
            wf.append(b)
            Ei.append(a)
        k+=1
        if k > 10000:   # break infinity loop if there is no relevant 
            break       # windingfactor of the actual winding layout 

    phase, sequence = calc_phaseangle_starvoltage(Ei)
    for k in range(len(sequence)):
        wf[k] = [sequence[k] * s for s in wf[k]]
    
    return nu, Ei, wf, phase
    
   

def calc_star(Q, S, p, nu):
    '''
    Calculates the slot voltage vectors for the given winding layout 

    Parameters
    ----------
    Q :      integer
             number of slots
    S :      list of lists
             winding layout
    p :      integer
             number of pole pairs
    nu:      integer
             harmonic number for calculation
             
    Returns
    -------
    return Ei: list
               voltage vectors for every phase and every slot
               Ei[phase][slot]
    return kw: list
               winding factor (absolute value) for every phase
               kw[phase]
    '''
    S2 = []
    for k in range(len(S)):
        S2.append( [item for sublist in S[k] for item in sublist] )  # flatten layers
        S2[k] = sorted(S2[k], key=abs)  # sort to abs values (slots in sequence -1,2,2,-3,...


    Ei = []
    kw = []
    for s in S2:
        alpha = 2.*nu*p*np.pi/(Q) * np.abs(s)
        
        for k in range(len(s)):
            if s[k] < 0:
                alpha[k] += np.pi           # negative Zeiger umklappen
        
        a = ( np.exp(1j*alpha) )            # Spannungsvektoren berechnen
        if np.sum(a) != 0.0:
            b = np.abs(np.sum(a)) / np.sum(np.abs(a))
        else:
            b = np.array(0.0)
        Ei.append( a.tolist() )
        kw.append( b.tolist() )
    return Ei, kw



def calc_MMK(Q, m, S, N = 3601, angle = 0):
    '''
    Calculates the magneto-motoric force (MMK) 

    Parameters
    ----------
    Q :      integer
             number of slots
    m :      integer
             number of phases
    S :      list of lists
             winding layout
    N :      integer
             number of values for the MMK curve
    angle:   float
             actual phase of the current system
             
    Returns
    -------
    return MMK:   list
                  MMK curve
    return theta: list
                  effective current for each slot
    '''
    S2 = []
    for k in range(len(S)):
        S2.append( [item for sublist in S[k] for item in sublist] )  # flatten layers
        S2[k] = sorted(S2[k], key=abs)  # sort to abs values (slots in sequence -1,2,2,-3,...
        
    # step function
    def h(x):
        return np.where(x<0., 0., 1.)

    phi = np.linspace(0, 2*np.pi, N)
    I = []
    km = 2 if m%2 == 0 else 1
    for k in range(m):
        I.append( np.cos( 2*np.pi/(m*km)*k - angle ) )
    theta = np.zeros(Q)
    for k1 in range(m):
        phase = S2[k1]
        for k2 in range(len(phase)):
            idx = np.abs(phase[k2])
            VZ = np.sign(phase[k2])
            theta[idx-1] += VZ*I[k1]
    MMK = np.zeros(np.shape(phi))
    for k in range(Q):
        MMK += theta[k] * h(phi-2*np.pi/Q*k)
    MMK -= np.mean(MMK[:-1])
    phi = phi/max(phi)*Q
    return phi.tolist(), MMK.tolist(), theta.tolist()



def DFT(vect):
    """
    Harmonic Analyses
    
    Parameters
    ----------
    vect  : array_like
            curve (time signal)
             
    Returns
    -------
    return : complex ndarray
             complex spectrum
    """
    #  vect = np.array(vect,float)
    N = len(vect)
    yy = 2./N*np.fft.fft(vect)
    yy[0] = np.mean(vect)
    return yy  



