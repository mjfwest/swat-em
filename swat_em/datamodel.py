# -*- coding: utf-8 -*-

# Provides a central class for data 
import json
import os
import fractions
import math
#  import numpy as np
import copy
import string
import gzip
#  import pdb


from swat_em import analyse


class datamodel:
    '''
    Provides a central place for all data. All analysis functions are
    connect with this class.
    ''' 
    file_format = 1
    machinedata_keys = ['Q', 'p', 'm', 'phases', 'wstep']
    results_keys = ['q', 'nu_el', 'Ei_el', 'kw_el', 'phaseangle_el', 
                    'nu_mech', 'Ei_mech', 'kw_mech', 'phaseangle_mech',
                    'valid', 'error']
    
    def __init__(self):
        self.reset_data()
        self.reset_results()
        #  self.reset_config()
        self.filename = None
        self.actual_state_saved = False
        
    def set_filename(self, filename):
        self.filename = filename
    
    def reset_data(self):
        '''
        resets all data of the datamodel
        '''
        self.machinedata = {}
        for key in self.machinedata_keys:
            self.machinedata[key] = None
        self.actual_state_saved = False
    
    def reset_results(self):
        self.results = {}
        for key in self.results_keys:
            self.results[key] = None
        self.actual_state_saved = False
    
    def set_config(self, config):
        self.config = config
    
    def set_machinedata(self, Q = None, p = None, m = None):
        '''
        setting the machine data 

        Parameters
        ----------
        Q :      integer
                 number of slots
        p :      integer
                 number of pole pairs
        m:       integer
                 number of phases
        '''
        if Q:
            self.machinedata['Q'] = int(Q)
        if p:
            self.machinedata['p'] = int(p)
        if m:
            self.machinedata['m'] = int(m)
        self.actual_state_saved = False
        
        
    def set_phases(self, S, wstep = None):
        '''
        setting the winding layout 

        Parameters
        ----------
        S : list of lists
            winding layout for every phase, for example:
            S = [[1,-2], [3,-4], [5,-6]]. This means there are 3 phases
            with phase 1 in in slot 1 and in slot 2 with negativ winding
            direction.
        wstep : winding step (slots as unit)
        ''' 
        self.machinedata['phases'] = S
        self.actual_state_saved = False
        self.set_machinedata(m = len(S))
        self.machinedata['phasenames'] = [string.ascii_uppercase[k] for k in range(len(S))]
        if wstep:
            self.machinedata['wstep'] = int(wstep)
        

    def set_valid(self, valid, error):
        self.results['valid'] = valid
        self.results['error'] = error


    def get_num_layers(self):
        '''
        Returns the number of layers of the actual winding layout
        '''
        l = 1
        for p in self.machinedata['phases']:
            if len(p[1]) > 1:
                l = 2
        return l

        
    def get_basic_characteristics(self):
        '''
        Returns the basic charactericits of the winding as 
        dictionary and a string
        '''
        if not 'basic_char' in self.results.keys():
            bc = analyse.get_basic_characteristics(
                self.machinedata['Q'],
                2*self.machinedata['p'],
                self.machinedata['m'],
                self.machinedata['phases'])
            self.results['basic_char'] = bc
        else:
            bc = self.results['basic_char']
        txt = []
        txt.append('q: ' + str(bc['q']))
        txt.append('periodic: ' + str(bc['a']))
        
        txt.append('kw1: ')
        for k in bc['kw1']:
            txt[-1] += ( str(round(k, 3)) + ', ' )
        txt[-1] = txt[-1][:-2]
        
        txt.append('lcm(Q,P): ' + str(bc['lcmQP']))
        
        txt.append('periodic base winding t: ' + str(bc['t']))
        txt.append('parallel conection a: ' + str(bc['a']))
        if bc['sym'] and bc['a']:
            txt.append('symmetric: ' + str(bc['sym']))
        else:            
            #  txt.append('<span style=\" font-size:8pt; font-weight:600; color:#ff0000;\" >')
            t = '<span style=\" color:#ff0000;\" >'
            t += 'symmetric: ' + str(bc['sym'])
            t += '</span>'
            txt.append(t)

        if self.results['error']:
            t = '<span style=\" color:#ff0000;\" >'
            t += 'ERROR: ' + str(self.results['error'])
            t += '</span>'
            txt.append(t)

        
        txt = '<br>'.join(txt)  # line break in html
        return bc, txt
        
    def calc_q(self):
        self.results['q'] = analyse.calc_q(self.machinedata['Q'], 
                                self.machinedata['p'],
                                self.machinedata['m'])
        
        
    def analyse_wdg(self):
        '''
        analyses the winding (winding factor etc.)
        ''' 
        self.reset_results()
        
        # number of slots per pole and phase
        self.q = fractions.Fraction(self.machinedata['Q'] / (
            self.machinedata['m']*2*self.machinedata['p'])).limit_denominator(100)
        self.results['q'] = self.q
        self.n = self.q.denominator
        self.z = self.q.numerator
        
        # base winding
        self.results['t'] = math.gcd(self.machinedata['Q'], self.machinedata['p'])
        
        # electrical winding factor
        a, b, c, d = analyse.calc_kw(
            self.machinedata['Q'], 
            self.machinedata['phases'], 
            self.machinedata['p'], 
            self.config['N_nu_el'],
            self.config )
        self.results['nu_el'] = a
        self.results['Ei_el'] = b
        self.results['kw_el'] = c
        self.results['phaseangle_el'] = d
        
        # mechanical winding factor
        a, b, c, d = analyse.calc_kw(
            self.machinedata['Q'], 
            self.machinedata['phases'], 
            1.0, 
            self.config['N_nu_mech'],
            self.config )
        self.results['nu_mech'] = a
        self.results['Ei_mech'] = b
        self.results['kw_mech'] = c
        self.results['phaseangle_mech'] = d
        
        # winding symmetric?
        self.results['wdg_is_symmetric'] = analyse.wdg_is_symmetric(self.results['Ei_el'],
            self.machinedata['m'])
        #  print(self.results['wdg_is_symmetric'])
        
        # periodicity of the winding (radial force, parallel connection)? 
        self.results['wdg_periodic'] = analyse.wdg_get_periodic(self.results['Ei_el'], self.machinedata['phases'])
        #  print(self.results['wdg_periodic'])
        self.actual_state_saved = False
        
        # MMK
        phi, MMK, theta = analyse.calc_MMK(self.machinedata['Q'],
                                           self.machinedata['m'],
                                           self.machinedata['phases'])
        nu = list(range(self.config['max_nu_MMK']+1))
        HA = analyse.DFT(MMK[:-1])[:self.config['max_nu_MMK']+1]
        self.results['MMK'] = {}
        self.results['MMK']['MMK'] = MMK
        self.results['MMK']['phi'] = phi
        self.results['MMK']['theta'] = theta
        self.results['MMK']['nu'] = nu
        self.results['MMK']['HA'] = HA.tolist()
        
        bc, bc_txt = self.get_basic_characteristics()
        self.results['basic_char'] = bc

        

    def save_to_file(self, fname):
        '''
        Saves the data to file. 

        Parameters
        ----------
        fname :  string
                 file name
        ''' 
        def complex2tuple_1(cplx):
            '''
            converts complex data to tuple of (real, imag)-part
            
            Parameters
            ----------
            fname : list
                    with complex numbers
            '''
            for k1 in range(len(cplx)):
                        cplx[k1] = (cplx[k1].real, cplx[k1].imag)
            return cplx
       
        def complex2tuple_3(cplx):
            '''
            converts complex data to tuple of (real, imag)-part
            
            Parameters
            ----------
            fname : list(list(list))
                    3 nested lists with complex numbers
            '''
            for k1 in range(len(cplx)):
                for k2 in range(len(cplx[k1])):
                    for k3 in range(len(cplx[k1][k2])):
                        cplx[k1][k2][k3] = (cplx[k1][k2][k3].real, cplx[k1][k2][k3].imag)
            return cplx
        
        M = {}
        M['file_format'] = self.file_format
        M['machinedata'] = self.machinedata
        #  M['config'] = self.config
        M['results'] = copy.deepcopy(self.results)
        
        # convert lists with complex numbers to tuple with real and imag
        if 'Ei_el' in M['results'].keys():
            M['results']['Ei_el'] = complex2tuple_3(M['results']['Ei_el'])
        
        if 'Ei_mech' in M['results'].keys():
            M['results']['Ei_mech'] = complex2tuple_3(M['results']['Ei_mech'])
        
        if 'MMK' in M['results'].keys():
            M['results']['MMK']['HA'] = complex2tuple_1(M['results']['MMK']['HA'])
        
        # convert fractional number
        if 'q' in M['results'].keys():
            M['results']['q'] = str(M['results']['q'])
            
        if 'basic_char' in M['results'].keys():
            if 'q' in M['results']['basic_char'].keys():
                M['results']['basic_char']['q'] = str(M['results']['basic_char']['q'])
        
        # save as compressed file
        with gzip.GzipFile(fname, 'w') as f:
            s = json.dumps(M, indent = 2)                  # string
            f.write(s.encode('utf-8'))           # bytes        
            
        # save as ASCII file
        #  with open(fname, 'w') as f:
            #  json.dump(M, f, indent = 2)
        self.actual_state_saved = True


    def load_from_file(self, fname):
        '''
        Load data from file. 

        Parameters
        ----------
        fname :  string
                 file name
        ''' 
        
        def tuple2complex_1(cplx):
            '''
            converts tuple of (real, imag) to complex number
            
            Parameters
            ----------
            fname : list
                    with complex numbers
            '''
            for k1 in range(len(cplx)):
                        cplx[k1] = cplx[k1][0] + 1j*cplx[k1][1]
            return cplx
        
        def tuple2complex_3(cplx):
            '''
            converts tuple of (real, imag) to complex number
            
            Parameters
            ----------
            fname : list(list(list))
                    3 nested lists with tuples
            '''
            for k1 in range(len(cplx)):
                for k2 in range(len(cplx[k1])):
                    for k3 in range(len(cplx[k1][k2])):
                        cplx[k1][k2][k3] = cplx[k1][k2][k3][0] + 1j*cplx[k1][k2][k3][1]
            return cplx
        
        
        if os.path.isfile(fname):
            self.reset_results()
            # load ASCII file
            #  with open(fname) as f:
                #  M = json.load(f)
            
            # load compressed file
            with gzip.GzipFile(fname) as f:  # gzip
                s = f.read()                    # bytes
                s = s.decode('utf-8')           # string
                M = json.loads(s)               # data  
            
            self.machinedata = M['machinedata']
            
            # load config
            #  self.config = M['config']
            
            # convert lists with tuple of real and imag to complex number
            if 'Ei_el' in M['results'].keys():
                M['results']['Ei_el'] = tuple2complex_3(M['results']['Ei_el'])
            
            if 'Ei_mech' in M['results'].keys():
                M['results']['Ei_mech'] = tuple2complex_3(M['results']['Ei_mech'])
            
            if 'MMK' in M['results'].keys():
                M['results']['MMK']['HA'] = tuple2complex_1(M['results']['MMK']['HA'])
            
            # convert fractional number
            if 'q' in M['results'].keys():
                M['results']['q'] = fractions.Fraction(M['results']['q'])
            
            if 'basic_char' in M['results'].keys():
                if 'q' in M['results']['basic_char'].keys():
                    M['results']['basic_char']['q'] = fractions.Fraction(M['results']['basic_char']['q'])
            
                self.results = copy.deepcopy(M['results'])
            self.actual_state_saved = True










