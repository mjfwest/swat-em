# -*- coding: utf-8 -*-
'''
Provides a central class for data 
'''
import json
import os
import fractions
import math
import copy
import string
import gzip
import gc
from swat_em import analyse
from swat_em import report as rep
from swat_em import wdggenerator
from swat_em.config import config




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
        #  self.filename = None
        self.actual_state_saved = False
        
    #  def set_filename(self, filename):
        #  self.filename = filename
    
    def reset_data(self):
        '''
        resets all data of the datamodel
        '''
        self.title = ''
        self.notes = ''
        self.machinedata = {}
        for key in self.machinedata_keys:
            self.machinedata[key] = None
        self.machinedata['turns'] = 1
        self.actual_state_saved = False
    
    def reset_results(self):
        self.results = {}
        for key in self.results_keys:
            self.results[key] = None
        self.actual_state_saved = False
    
    def set_title(self, title):
        self.title = title
    
    def get_title(self):
        return self.title
    
    def get_notes(self):
        return self.notes
        
    def set_notes(self, notes):
        self.notes = notes
    
    #  def set_config(self, config):
        #  self.config = config
    
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
        
        
    def set_phases(self, S, turns = 1, wstep = None):
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
        self.machinedata['turns'] = turns
        self.actual_state_saved = False
        self.set_machinedata(m = len(S))
        self.machinedata['phasenames'] = [string.ascii_uppercase[k] for k in range(len(S))]
        if wstep:
            self.machinedata['wstep'] = int(wstep)
        

    def set_valid(self, valid, error):
        self.results['valid'] = valid
        self.results['error'] = error
    
    
    def genwdg(self, Q, P, m, w, layers, turns = 1):
        '''
        Generates a winding layout and stores it in the datamodel

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
        turns  : integer
                 number of turns per coil

        '''
        
        self.set_machinedata(Q, int(P/2), m)
        wdglayout = wdggenerator.genwdg(Q, P, m, w, layers)
        
        self.set_phases(S = wdglayout['phases'], turns = turns, wstep = wdglayout['wstep'])
        self.set_valid(valid = wdglayout['valid'], error = wdglayout['error'])
        self.analyse_wdg()
        self.actual_state_saved = True # Simulate save state


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
                self.machinedata['phases'],
                self.machinedata['turns'])
            self.results['basic_char'] = bc
        else:
            bc = self.results['basic_char']

        dat = [['Number of slots ',    rep.italic('Q: '),  str(self.machinedata['Q'])],
               ['Number of poles ',    rep.italic('2p: '), str(2*self.machinedata['p'])],
               ['Number of phases ',   rep.italic('m: '),  str(self.machinedata['m'])],
               ['slots per 2p per m ', rep.italic('q: '),  str(bc['q'])]]
        for i, k in enumerate(bc['kw1']):
            dat.append(['winding factor (m={}) '.format(i+1), rep.italic('kw1: '), str(round(k,3)) ])
        dat.append(['lcm(Q, P) ', '', str(bc['lcmQP'])])
        dat.append(['periodic base winding ', rep.italic('t: '), str(bc['t'])])
        
        a_ = [str(i) for i in analyse.Divisors(bc['a'])]
        dat.append(['parallel connection ', rep.italic('a: '), ','.join(a_)])
        if bc['sym'] and bc['a']:
            dat.append(['symmetric ', '', str(bc['sym'])])
        else:
            dat.append([rep.red('symmetric '), '', rep.red(str(bc['sym']))])
        txt = rep.table(dat)
        if self.results['error']:
            txt.append(rep.red('error: ' + str(self.results['error'])))
        
        if len(self.notes) > 0:
            #  txt.append('<br><br>' + rep.bold(Notes) + ':<br>')
            txt.append(rep.bold('<br><br>Notes<br>'))
            txt.append(rep.italic(self.notes))
        
        txt = ''.join(txt)
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
            self.machinedata['turns'],
            self.machinedata['p'], 
            config['N_nu_el'],
            config )
        self.results['nu_el'] = a
        self.results['Ei_el'] = b
        self.results['kw_el'] = c
        self.results['phaseangle_el'] = d
        
        # mechanical winding factor
        a, b, c, d = analyse.calc_kw(
            self.machinedata['Q'], 
            self.machinedata['phases'],
            self.machinedata['turns'], 
            1.0, 
            config['N_nu_mech'],
            config )
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
                                           self.machinedata['phases'],
                                           self.machinedata['turns'])
        nu = list(range(config['max_nu_MMK']+1))
        HA = analyse.DFT(MMK[:-1])[:config['max_nu_MMK']+1]
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



class project:
    '''
    Provides all data-objects (all winding in workspace)
    '''
    file_format = 2
    def __init__(self):
        self.models = []
        self.filename = None
        self.undo_state = []
        self.redo_state = []
        
    def save_undo_state(self):
        '''saves the actual state of the models for undo function'''
        self.undo_state.append(copy.deepcopy(self.models))
    
    def save_redo_state(self):
        '''saves the actual state of the models for redo function'''
        self.redo_state.append(copy.deepcopy(self.models))
    
    def reset_undo_state(self):
        '''delete all existings undo state saves - no undo possible any more'''
        self.undo_state = []
    
    def reset_redo_state(self):
        '''delete all existings redo state saves - no redo possible any more'''
        self.redo_state = []
    
    def get_num_undo_state(self):
        '''return the number of undo state saves = number of possible undo opserations'''
        return len(self.undo_state)
    
    def get_num_redo_state(self):
        '''return the number of redo state saves = number of possible redo opserations'''
        return len(self.redo_state)
    
    def undo(self):
        '''restores the last state'''
        if self.get_num_undo_state() > 0:
            self.models = self.undo_state.pop(-1)
            gc.collect()  # force to free memory
    
    def redo(self):
        '''restores the last state'''
        if self.get_num_redo_state() > 0:
            self.models = self.redo_state.pop(-1)
            gc.collect()  # force to free memory
    
    def set_filename(self, filename):
        '''saves the filename if a the data is load from file or
        stored to a file'''
        self.filename = filename
    
    def gen_model_name(self):
        '''
        creates an unique title for a model
        '''
        titles = [data.title for data in self.models]
        i = 0
        while True:
            name = 'untitled' + str(i)
            if name not in titles:
                return name
            i += 1
    
    def add_model(self, data):
        '''
        adds 'data' model to project. Generates a unique title if there
        is no title in 'data'
        '''
        if data.title == '':
            name = self.gen_model_name()
            data.set_title(name)
            data.actual_state_saved = False
        self.models.append(data)
        
    def get_titles(self):
        '''returns the title of all models'''
        return [data.title for data in self.models]
    
    def get_num_models(self):
        '''returns the number of models in this project'''
        return len(self.models)
    
    def get_model_by_index(self, idx):
        '''returns the model with the index 'idx' '''
        return self.models[idx]

    def delete_model_by_index(self, idx):
        '''deletes the model with the index 'idx' '''
        del self.models[idx]
    
    def clone_by_index(self, idx):
        '''duplicates the model with the index 'idx' '''
        data = copy.deepcopy(self.models[idx])
        data.set_title(data.get_title() + '_copy')
        data.actual_state_saved = False
        self.add_model(data)

    def rename_by_index(self, idx, newname):
        '''change the title of the model with the index 'idx' 
        with name 'newname' '''
        self.models[idx].set_title(newname)
    
    def replace_model_by_index(self, newmodel, idx):
        '''replaces the model of index 'idx' with 'newmodel' '''
        self.models[idx] = newmodel

    def set_actual_state_saved(self):
        '''marks all models as saved'''
        for data in self.models:
            data.actual_state_saved = True

    def get_actual_state_saved(self):
        '''returns True if all data is saved'''
        for data in self.models:
            if not data.actual_state_saved:
                return False
        return True


    def save_to_file(self, fname):
        '''
        Saves the data to file. 

        Parameters
        ----------
        fname :  string
                 file name
        ''' 
        M = {}
        M['file_format'] = self.file_format
        M['models'] = []
        for data in self.models:
            N = {}
            N['machinedata'] = data.machinedata
            N['title'] = data.title
            N['notes'] = data.notes
            M['models'].append(N)
            
        # save as ASCII file
        with open(fname, 'w') as f:
            json.dump(M, f, indent = 2)
        self.actual_state_saved = True



    def load_from_file(self, fname):
        '''
        Load data from file. 

        Parameters
        ----------
        fname :  string
                 file name
        ''' 
        try:
            if os.path.isfile(fname):
                with open(fname) as f:
                    M = json.load(f)
        except:
            # file_format 1 is saved compressed
            import gzip
            with gzip.GzipFile(fname) as f:     # gzip
                s = f.read()                    # bytes
                s = s.decode('utf-8')           # string
                M = json.loads(s)               # data  
        
        if M['file_format'] == 1:
            self.models = []
            data = datamodel()
            data.machinedata = M['machinedata']
            if 'turns' not in data.machinedata.keys():
                data.machinedata['turns'] = 1
            data.analyse_wdg()
            self.add_model(data)
            self.set_actual_state_saved()
        
        elif M['file_format'] == 2:
            self.models = []
            for m in M['models']:
                data = datamodel()
                data.machinedata = m['machinedata']
                data.set_title(m['title'])
                data.set_notes(m['notes'])
                data.analyse_wdg()
                self.add_model(data)
            self.set_actual_state_saved()
        self.set_filename(fname)


