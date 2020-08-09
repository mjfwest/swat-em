# -*- coding: utf-8 -*-
"""
Provides functions for analyzing windings
"""
import numpy as np
import fractions
import math
from collections import Counter, deque


def calc_q(Q, p, m):
    return fractions.Fraction(Q / (m * 2 * p)).limit_denominator(100)


def get_basic_characteristics(Q, P, m, S, turns=1, Qes=0):
    q = fractions.Fraction((Q - Qes) / (m * P)).limit_denominator(100)

    S2 = _flatten(S)
    if hasattr(turns, "__iter__"):
        turns = _flatten(turns)
    for k in range(len(S2)):
        idx = np.argsort(np.abs(S2[k]))
        S2[k] = np.array(S2[k])[idx]
        if hasattr(turns, "__iter__"):
            turns[k] = np.array(turns[k])[idx]
    Ei, kw = calc_star(Q, S2, turns, P / 2, 1)

    a = wdg_get_periodic([Ei], S)
    a = a[0]  # phase 1
    sym = wdg_is_symmetric([Ei], m)
    t = math.gcd(int(Q), int(P / 2))
    lcmQP = int(np.lcm(int(Q), int(P)))
    valid, error = check_number_of_coilsides(S)
    if not valid:
        sym = False
    bc = {"q": q, "kw1": kw, "a": a, "sym": sym, "t": t, "lcmQP": lcmQP, "error": error}
    return bc


def double_linked_leakage(kw, nu, p):
    """
    Returns the coefficient of the double linkead leakage flux.

    Parameters
    ----------
    kw :     list or array
             mechanical winding factor
    nu :     list or array
             ordinal number with respect to the mechanical winding factor.
    p  :     integer
             number of pole pairs
             
    Returns
    -------
    return : float
             coefficient of the double linkead leakage flux
    """
    kw = np.abs(kw)
    kw1 = kw[list(nu).index(p)]
    sigma_d = np.sum((kw / (nu / p)) ** 2)
    sigma_d -= (kw1) ** 2

    if kw1 != 0:
        sigma_d /= kw1 ** 2
    else:
        sigma_d = -1
    return sigma_d


def wdg_get_periodic(Ei, S):
    """
    Returns the symmetry factor for the winding 

    Parameters
    ----------
    Ei :     list of lists of lists
             voltage vectors for every phase and every slot
             Ei[nu][phase][slot]
    S :      list of lists
             winding layout
             
    Returns
    -------
    return : list
             symmetry factor for each phase. 
             1 if there is no periodicity
             2 if half of the machine is smallest symmetric part and so on...
    """
    if len(Ei) == 0:
        return 1
    if len(Ei[0]) == 0:
        return 1

    periodic = []
    # for each phase
    for km in range(len(S)):
        ei = Ei[0][km]  # only for fundamental
        S2 = S[km]
        S2 = [item for sublist in S2 for item in sublist]  # flatten layers
        ei_pos = []
        ei_neg = []
        for i, s in enumerate(S2):
            if s > 0:
                ei_pos.append(ei[i])  # phasors of pos. coil sides
            else:
                ei_neg.append(ei[i])
        if len(ei_pos) != len(ei_neg):
            periodic.append(1)
        else:
            a_max = 0
            #  a_list = [1]
            for k in range(
                len(ei_pos)
            ):  # all combinations of connections of coil sides
                #                angles = np.angle(ei_pos + np.roll(ei_neg, k))
                d = deque(ei_neg)
                d.rotate(k)
                angles = np.angle(ei_pos + np.array(d))
                angles = np.round(angles, 4)
                c = Counter(angles)
                a = min(c.values())
                if a > a_max:
                    a_max = a
            periodic.append(a_max)
    return periodic


def wdg_is_symmetric(Ei, m):
    """
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

    """
    if len(Ei) == 0:
        return None
    if len(Ei[0]) == 0:
        return None
    ei = Ei[0]  # only for fundamental
    angles = [np.angle(sum(k)) / np.pi * 180 for k in ei]
    angles = np.round(angles, 4)
    length = [np.abs(sum(k)) for k in ei]

    if m % 2 == 0:  # shift all phasors to >180 for even number of phases
        # angles = np.array(angles)
        angles += 360
        angles -= np.min(angles)
        angles[angles < 180] += 360
    angles.sort()

    if m % 2 == 0:
        target_angle = 360 / (2 * m)
    else:
        target_angle = 360 / m
    diff = np.diff(angles)
    sym = True
    # Test for phase angles
    for d in diff:
        if not math.isclose(target_angle, d, rel_tol=1e-02, abs_tol=1e-02):
            sym = False
    # Test for amplitude
    for k in range(1, len(length)):
        if not math.isclose(length[0], length[k], rel_tol=1e-02, abs_tol=1e-02):
            sym = False
    return sym


def check_number_of_coilsides(S):
    S2 = _flatten(S)
    valid = True
    error = ""
    # test if the number of positve and negative coil sides are equal
    for k in range(len(S2)):
        s = S2[k]
        pos = 0
        neg = 0
        for w in s:
            if w > 0:
                pos += 1
            elif w < 0:
                neg += 1
        if pos != neg:
            error += "Phase {} has {} postive and {} negative coil sides".format(
                k + 1, pos, neg
            )
            valid = False

    l = [len(s) for s in S2]
    if len(set(l)) != 1:
        error = "Not all phases have the same number of coil sides:<br>"
        for k in range(len(S)):
            error += "Phase {} hat {} coilsides<br>".format(k + 1, l[k])
    return valid, error


def calc_phaseangle_starvoltage(Ei):
    """
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
    """
    phaseangle = []
    for knu in Ei:  # for every nu
        phaseangle.append([])
        angle = [np.angle(sum(km)) * 180 / np.pi for km in knu]  # for every phase
        for a in angle:
            while a < 0:
                a += 360.0
            phaseangle[-1].append(a)

    sequence = []
    for p in phaseangle:
        if len(p) > 1:
            if p[1] > p[0]:
                sequence.append(1)
            else:
                sequence.append(-1)
        else:
            sequence.append(0)
    #  if sequence[0] < 0:  # related to the fundamental
    #  sequence = [-k for k in sequence]

    return phaseangle, sequence


def calc_kw(Q, S, turns, p, N_nu, config):
    """
    Calculates the windingfactor, the slot voltage vectors. The 
    harmonic numbers are generated automatically.

    Parameters
    ----------
    Q :      integer
             number of slots
    S :      list of lists
             winding layout
    turns :  number or list of lists (shape of 'S')
             number of turns. If turns is a list of lists, for each
             coil side a specific number of turns is used
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
    """
    #  S = [item for sublist in S for item in sublist]  # flatten layers
    nu = []  # order
    wf = []  # winding factor
    Ei = []  # slot voltage vectors

    S2 = _flatten(S)
    if hasattr(turns, "__iter__"):
        turns = _flatten(turns)
    for k in range(len(S2)):
        idx = np.argsort(np.abs(S2[k]))
        S2[k] = np.array(S2[k])[idx]
        if hasattr(turns, "__iter__"):
            turns[k] = np.array(turns[k])[idx]

    k = 1
    while len(wf) < N_nu:
        a, b = calc_star(Q, S2, turns, p, k)
        if np.all(np.abs(b) > config["kw_min"]):
            nu.append(k)
            wf.append(b)
            Ei.append(a)
        k += 1
        if k > 10000:  # break infinity loop if there is no relevant
            break  # windingfactor of the actual winding layout

    phase, sequence = calc_phaseangle_starvoltage(Ei)
    for k in range(len(sequence)):
        wf[k] = [sequence[k] * s if sequence[k] != 0 else s for s in wf[k]]

    return nu, Ei, wf, phase


def calc_kw_by_nu(Q, S, turns, p, nu):
    """
    Calculates the windingfactor for the given harmonic number

    Parameters
    ----------
    Q :      integer
             number of slots
    S :      list of lists
             winding layout
    turns :  number or list of lists (shape of 'S')
             number of turns. If turns is a list of lists, for each
             coil side a specific number of turns is used
    p :      integer
             number of pole pairs
    nu:      integer
             harmonic number
             
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
    """
    wf = []  # winding factor
    Ei = []  # slot voltage vectors
    if not test_phases(S):
        return None

    S2 = _flatten(S)
    if hasattr(turns, "__iter__"):
        turns = _flatten(turns)
    for k in range(len(S2)):
        idx = np.argsort(np.abs(S2[k]))
        S2[k] = np.array(S2[k])[idx]
        if hasattr(turns, "__iter__"):
            turns[k] = np.array(turns[k])[idx]

    a, b = calc_star(Q, S2, turns, p, nu)
    wf.append(b)
    Ei.append(a)

    phase, sequence = calc_phaseangle_starvoltage(Ei)
    for k in range(len(sequence)):
        wf[k] = [sequence[k] * s if sequence[k] != 0 else s for s in wf[k]]

    return wf[0]


def test_phases(S):
    """
    Test if there is data in phases
    """
    if S is None:
        return None
    valid = True
    for km in range(len(S)):
        if len(S[km][0]) == 0 and len(S[km][0]) == 0:
            valid = False
    return valid


def calc_star(Q, S, turns, p, nu):
    """
    Calculates the slot voltage vectors for the given winding layout 

    Parameters
    ----------
    Q :      integer
             number of slots
    S :      list of lists
             winding layout
    turns :  number or list of lists (shape of 'S')
             number of turns. If turns is a list of lists, for each
             coil side a specific number of turns is used
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
    """
    S2 = S
    Ei = []
    kw = []
    for i, s in enumerate(S2):
        turn = turns[i] if hasattr(turns, "__iter__") else turns
        alpha = 2.0 * nu * p * np.pi / Q * np.abs(s)
        alpha[s < 0] += np.pi

        a = turn * np.exp(1j * alpha)  # Spannungsvektoren berechnen
        b = np.abs(sum(a)) / sum(np.abs(a)) if sum(a) != 0.0 else 0.0
        Ei.append(a)
        kw.append(b)
    return Ei, kw


def calc_MMK(Q, m, S, turns=1, N=3601, angle=0):
    """
    Calculates the magneto-motoric force (MMK) 

    Parameters
    ----------
    Q :      integer
             number of slots
    m :      integer
             number of phases
    S :      list of lists
             winding layout
    turns :  number or list of lists (shape of 'S')
             number of turns. If turns is a list of lists, for each
             coil side a specific number of turns is used
    N :      integer
             number of values for the MMK curve
    angle:   float
             actual phase of the current system in deg
             
    Returns
    -------
    return MMK:   list
                  MMK curve
    return theta: list
                  effective current for each slot
    """
    S2 = _flatten(S)
    if hasattr(turns, "__iter__"):
        turns2 = _flatten(turns)
    for k in range(len(S)):
        idx = np.argsort(np.abs(S2[k]))
        S2[k] = np.array(S2[k])[idx]
        if hasattr(turns, "__iter__"):
            turns2[k] = np.array(turns2[k])[idx]

    def h(x):
        """step function"""
        return np.where(x < 0.0, 0.0, 1.0)

    phi = np.linspace(0, 2 * np.pi, N)
    I = []
    km = 2 if m % 2 == 0 else 1
    for k in range(m):
        I.append(np.cos(2 * np.pi / (m * km) * k - angle / 180 * np.pi))
    theta = np.zeros(Q)
    for k1 in range(m):
        phase = S2[k1]

        for k2 in range(len(phase)):
            if hasattr(turns, "__iter__"):
                turn = turns2[k1][k2]
            else:
                turn = turns
            idx = np.abs(phase[k2])
            idx = idx - Q if idx > Q else idx
            VZ = np.sign(phase[k2])
            theta[idx - 1] += VZ * I[k1] * turn
    MMK = np.zeros(phi.shape)
    for k in range(Q):
        MMK += theta[k] * h(phi - 2 * np.pi / Q * k)
    MMK -= np.mean(MMK[:-1])
    phi = phi / np.max(phi) * Q
    return phi, MMK, theta


def calc_radial_force_modes(MMK, m, num_modes=4):
    """
    Calculates the radial force modes based on the 
    magneto-motoric force (MMK). The results includes also the modes
    with a multiple of the phase-number (which aren't there if the
    machine is star-connected). 

    Parameters
    ----------
    MMK :    array_like
             waveform of the magneto-motoric foce
    m :      integer
             number of phases
             
    Returns
    -------
    return MMK:   list
                  radial force modes
    """
    HA = np.abs(DFT(np.array(MMK[:-1]) ** 2))

    HA_max = np.max(HA)
    modes = []
    for k in range(1, len(HA)):
        if HA[k] > 0.01 * HA_max:
            modes.append(k)
        if len(modes) >= num_modes:
            break

    # include the modes evoked by the multiply of the phase-number
    # (this is the case if the winding is not star connected)
    for k in range(len(modes)):
        modes.append(int(m * modes[0]))
        if k >= num_modes:
            break
    modes = list(set(modes))  # remove duplicates
    modes.sort()
    modes = modes[:num_modes]

    return modes


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
    yy = 2.0 / N * np.fft.fft(vect)
    yy[0] = np.mean(vect)
    return yy[: N // 2]


def _get_float(txt):
    """
    returns the floating point number from string
    
    Parameters
    ----------
    txt  : string
           string of the number
             
    Returns
    -------
    return : float or None-type
             number from txt
             None if conversion is not possible
    """
    try:
        return float(txt.replace(",", "."))
    except:
        return None


def _flatten(l):
    l2 = []
    for kl in l:
        l2.append([item for sublist in kl for item in sublist])
    return l2


def Divisors(n):
    """
    returns a list of all divisors of the integer n
    """
    divisors = []
    i = 1
    while i <= n:
        if n % i == 0:
            divisors.append(i)
        i = i + 1
    return divisors


class create_wdg_overhang:
    def __init__(self, S, Q, num_layers):
        """
        Generate the winding overhang (connection of the coil sides).

        Parameters
        ----------
        S :                     list of lists
                                winding layout
        Q :                     integer
                                number of slots
        num_layers :            integer
                                number winding layers
        """
        self.S = S
        self.Q = Q
        self.num_layers = num_layers

    def diff_and_direct(self, start, end):
        """
        Returns the distance between two coil sides and the direction
        of the coil.

        Parameters
        ----------
        start : integer
                Coil side 1
        end   : integer
                Coil side 2 which is connected to coil side 1
                 
        Returns
        -------
        diff : integer 
               distance between S1 and S2 in slot count
        direct : integer
                 Direction of the coil 
                 +1 means coil from left to right
                 -1 means coil from right to left
        """
        Q = self.Q
        if end > start:
            if abs(end - start) > Q / 2:
                diff = start - end + Q
                direct = -1
            else:
                diff = end - start
                direct = 1
        else:
            if abs(end - start) > Q / 2:  # overflow
                diff = end + Q - start
                direct = 1
            else:
                diff = start - end
                direct = -1
        # prefer positive direction when possible (2p=2)
        if diff == Q / 2 and direct == -1:
            direct = 1
        return diff, direct

    def get_pos_neg_coil_sides(self, S, S2=None):
        """
        Returns the the position of the positive and negative
        coil sides from list. The coil sides are extracted from 'S'. 
        If 'S2' is given, than the positive coil sides are extracted
        from 'S' and the negative ones from 'S2'

        Parameters
        ----------
        S : list
            Coil sides
        S2 : list
             Coil sides
                 
        Returns
        -------
        Sp : list 
             Position of the positive coil sides
        Sn : list 
             Position of the negatuve coil sides
        """
        if S2 is None:
            Sp = S[S > 0]
            Sn = np.abs(S[S < 0])
        else:
            Sp = S[S > 0]
            Sn = np.abs(S2[S2 < 0])
        return Sp, Sn

    def get_dist_in_slots(self, S1, S2):
        """
        Returns the distance of the coilsides between S1 and S2.

        Parameters
        ----------
        S1 : integer
             Coil side
        S2 : Array
             Coil sides
                 
        Returns
        -------
        return : array 
                 distance between S1 and S2 in slot count
        """
        dist_slots = []
        direct = []
        for k in range(len(S2)):
            a, b = self.diff_and_direct(S1, S2[k])
            dist_slots.append(a)
            direct.append(b)
        return dist_slots, direct

    def get_overhang(self, wstep=None):
        """
        Returns the winding overhang (connection of the coil sides).

        Parameters
        ----------
        wstep : integer or list of integers
                Winding step(s) to apply. If not given the winding
                overhang gets minimized with different winding steps.
                 
        Returns
        -------
        return : list 
                 Winding connections for all phases, len = num_phases,
                 format: [[(from_slot, to_slot, stepwidth, direction), ()], [(), ()], ...]
                 from_slot: slot with positive coil side of the coil
                 to_slot:   slot with negative coil side of the coil
                 stepwidth: distance between from_slot to to_slot
                 direction: winding direction (1: from left to right, -1: from right to left)
                 layer: tuple of the layer of 'from_slot' and 'to_slot' 
        """
        self.wstep = wstep
        if wstep is not None:
            if hasattr(self.wstep, "__iter__"):
                self.wstep = list(self.wstep)
            else:
                self.wstep = list([self.wstep])
            self.wstep.sort()

        def get_connection(Sp, Sn, layer):
            """
            Returns the connection of coils from positive coil sides 'Sp'
            and negative coil sides 'Sn'
            """
            if len(Sp) != len(Sn):
                #  raise Exception('Number of positive and negative coils sides must be equal')
                print("Number of positive and negative coils sides must be equal")
                return []

            con = []
            for kp in range(len(Sp)):
                dist_slots, direct = self.get_dist_in_slots(Sp[kp], Sn)
                dist_min = np.argsort(dist_slots)  # idx

                idx = -1
                if wstep is None:
                    idx = dist_min[0]

                    # prefer positive direction
                    if direct[idx] < 0:
                        for i in range(1, len(dist_min)):
                            if dist_min[i] == dist_min[0] and direct[i] > 0:
                                idx = i
                                break
                else:
                    # shortest step
                    for i in dist_min:
                        if dist_slots[i] in self.wstep:
                            idx = i
                            break

                    # is there a step available in positive direction?
                    # this is not applicable for tooth coil windin
                    if self.num_layers == 1 and self.wstep != [1]:
                        dist_min2 = []
                        for i in dist_min:
                            if dist_slots[i] in self.wstep:
                                dist_min2.append(i)
                        for i in dist_min2:
                            if direct[i] > 0:
                                idx = i
                                break

                if idx == -1:
                    idx = dist_min[0]  # fallback
                    #  print('fallback')

                start, end = Sp[kp], Sn[idx]
                diff, direct = self.diff_and_direct(start, end)
                con.append([start, end, diff, direct, layer])
                Sn = np.delete(Sn, idx)
            return con

        head = []
        if self.num_layers == 1:
            for km in range(len(self.S)):
                S1 = np.array(self.S[km][0])
                Sp, Sn = self.get_pos_neg_coil_sides(S1)
                head.append(get_connection(Sp, Sn, layer=(0, 0)))
        elif self.num_layers == 2:
            for km in range(len(self.S)):
                S1 = np.array(self.S[km][0])
                S2 = np.array(self.S[km][1])
                Sp, Sn = self.get_pos_neg_coil_sides(S1, S2)
                head.append(get_connection(Sp, Sn, layer=(0, 1)))
                Sp, Sn = self.get_pos_neg_coil_sides(S2, S1)
                head[-1] += get_connection(Sp, Sn, layer=(1, 0))
        else:
            raise Exception("Number of layers >2 not implemented yet")

        return head
