# -*- coding: utf-8 -*-
'''
Provides functions for reports
''' 
import os
import tempfile
import numpy as np
import xlsxwriter
import re
from swat_em import analyse
from swat_em.config import config

def italic(txt):
    return '<i>' + txt + '</i>'


def table_header(data):
    txt = ['<tr>']
    for d in data:
        txt.append('<th>')
        txt.append(d)
        txt.append('</th>')
    txt.append('</tr>')
    return ''.join(txt)


def table_row(data, col = None):
    if col:
        txt = ['<tr bgcolor="{}">'.format(col)]
    else:
        txt = ['<tr>']
    for d in data:
        txt.append('<td>')
        txt.append(d)
        txt.append('</td>')
    txt.append('</tr>')
    return ''.join(txt)


def red(text):
    txt = ['<span style=\" color:#ff0000;\" >']
    txt.append(text)
    txt.append('</span>')
    return ''.join(txt)

def italic(text):
    return '<i>' + text + '</i>'

def bold(text):
    return '<b>' + text + '</b>'

def table(dat, header=[]):
    txt = ['<table style="width:100%">']
    if len(header) > 0:
        txt.append(table_header(header))
    col1 = '#FFFFFF'
    col2 = '#DDDADA'
    for i, d in enumerate(dat):
        col = col1 if i%2 != 0 else col2
        txt.append(table_row(d, col=col))
    
    txt.append('</table>')
    return txt

def num2str(number, maxlen=8):
    """
    Converts a number to string with max number of signs

    Parameters
    ----------
    number : scalar, array_like, string
             Number to convert
    maxlen : integer
             Max. length to convert
           
    Returns
    -------
    return : string / list of strings / ndarray of strings
             string with the number           
    """
    numstring = str(number)
    ematch = re.search('[eE].+', numstring)
    if ematch:
        # number in scientific
        exp = ematch.group()
        length = min(len(numstring), maxlen) - len(exp)
        numstring = numstring[:length] + exp
    else:
        numstring = numstring[:maxlen]
    if number >= 0.0:
        numstring = ' ' + numstring[:-1]
    return numstring


class HtmlReport:
    def __init__(self, data):
        """
        Class for creating HTML reports of the winding

        Parameters
        ----------
        data :   datamodel object
                 winding model for creating the report
        """  
        self.data = data
        self.template = os.path.abspath(os.path.join(os.path.dirname(__file__), 'template', 'report.html'))

    def _create_figures(self, tmpdir):
        """
        Creates all figures for the winding
        
        Parameters
        ----------
        tmpdir : string
                 name of the directory to store the figures
        """
        if not os.path.isdir(tmpdir):
            os.mkdir(tmpdir)
        self.data.plot_layout(os.path.join(tmpdir,'plot_layout.png'), res = config['plt']['res'])
        self.data.plot_star(os.path.join(tmpdir,'plot_star.png'), res = config['plt']['res'])
        self.data.plot_windingfactor(os.path.join(tmpdir,'plot_wf_el.png'), mechanical = False, res = config['plt']['res'])
        self.data.plot_windingfactor(os.path.join(tmpdir,'plot_wf_mech.png'), mechanical = True, res = config['plt']['res'])
        self.data.plot_MMK(os.path.join(tmpdir,'plot_MMK.png'), res = config['plt']['res'], phase = 0)

    def create(self, filename = None):
        """
        Generates the html-report and returns the name of the html file

        Returns
        -------
        return : string
                 The file name of the html-file which is stored in tmp directory
        """  
        if filename == None:
            self.tmpdir = tempfile.mkdtemp()
            self.filename = os.path.join(self.tmpdir, 'report.html')
        else:
            self.tmpdir = os.path.abspath(os.path.dirname(filename))
            self.filename = filename
        self.contentdir = os.path.splitext(self.filename)[0] + '-files'
        try:
            os.mkdir(self.contentdir)
        except:
            pass
        
        #  filename = '/media/ramdisk/report.html'
        #  tmpdir = '/media/ramdisk'   # for testing
        
        self._create_figures(self.contentdir)
        
        # create table of star of slots
        d = []
        ei = self.data.results['Ei_el'][0]    
        for km in range(len(ei)):
            A = np.abs( np.sum(ei[km]) )
            ph = np.angle( np.sum(ei[km]) )/np.pi*180
            d.append([str(km+1), str(round(A,1)), str(round(ph,1))])
        _table_star = '\n'.join(table(d, header = ['m', 'A', 'phase']))
        
        # create table of winding factor
        # electrical
        d = []
        nu = np.array(self.data.results['nu_el'])
        kw = np.array(self.data.results['kw_el'])
        header = ['nu'] + self.data.get_phasenames()
        for i, line in enumerate(kw):
            d.append( [str(nu[i])] + [str(round(k,3)) for k in line] )
        _table_wf_el = '\n'.join(table(d, header = header))
        
        # mechanical
        d = []
        nu = np.array(self.data.results['nu_mech'])
        kw = np.array(self.data.results['kw_mech'])
        header = ['nu'] + self.data.get_phasenames()
        for i, line in enumerate(kw):
            d.append( [str(nu[i])] + [str(round(k,3)) for k in line] )
        _table_wf_mech = '\n'.join(table(d, header = header))
        
        # create MMK
        d = []
        phi, MMK, theta = analyse.calc_MMK(self.data.get_num_slots(),
                           self.data.get_num_phases(),
                           self.data.get_phases(),
                           self.data.get_turns(),
                           angle = 0.0)       
        nu = np.array(self.data.results['MMK']['nu'])
        HA = analyse.DFT(MMK[:-1])[:len(nu)]
        A = np.abs(HA)
        header = ['nu', 'Amp', '[%]']
        for k in range(len(nu)):
            a = A[k]
            a_rel = 100.0/max(A)*a
            d.append([str(nu[k]), str(round(a, 3)), str(round(a_rel, 1))])
        _table_MMK = '\n'.join(table(d, header = header))

        
        # Write to template
        with open(self.template) as f:
            tmpl = f.readlines()
        
        _report = []
        for line in tmpl:
            line = line.strip()
            line = line.replace('{{ TITLE }}', self.data.get_title())
            line = line.replace('{{ NOTES }}', self.data.get_notes())
            
            line = line.replace('{{ plot_layout }}', os.path.join(self.contentdir, 'plot_layout.png'))
            txt, html = self.data.get_basic_characteristics()
            line = line.replace('{{ table_bc }}', html)
            
            line = line.replace('{{ plot_star }}', os.path.join(self.contentdir, 'plot_star.png'))
            line = line.replace('{{ table_star }}', _table_star)
            line = line.replace('{{ plot_wf_el }}', os.path.join(self.contentdir, 'plot_wf_el.png'))
            line = line.replace('{{ table_wf_el }}', _table_wf_el)
            line = line.replace('{{ plot_wf_mech }}', os.path.join(self.contentdir, 'plot_wf_mech.png'))
            line = line.replace('{{ table_wf_mech }}', _table_wf_mech)
            line = line.replace('{{ plot_MMK }}', os.path.join(self.contentdir, 'plot_MMK.png'))
            line = line.replace('{{ table_MMK }}', _table_wf_mech)
            
            _report.append(line)
        
        
        with open(self.filename, 'w') as f:
            f.write('\n'.join(_report))
        return self.filename
        

    def open_in_browser(self):
        """
        Open the html report in the webbrowser
        """
        if not os.path.isfile(self.filename):
            raise Exception('No html report available. Use the ".create()" before')
        else:
            import webbrowser
            webbrowser.open(self.filename)



def export_xlsx(fname, data):
    layout = True
    phasors = True
    windingfactor_el = True
    windingfactor_mech = True

    workbook = xlsxwriter.Workbook(fname)

    if layout:
        worksheet = workbook.add_worksheet('layout')

        i = 0
        cell_format = workbook.add_format({'font_size': 14})
        worksheet.write(i, 0, 'Windinglayout', cell_format)
        i += 1
        
        cell_format = workbook.add_format({'align': 'center'})
        for k in range(data.machinedata['Q']):
            worksheet.write(i, 1+k, k+1, cell_format)
        i += 1
        
        cell_format = workbook.add_format({'align': 'right'})
        worksheet.write(i-1, 0, 'slot No.', cell_format)
        for k in range(data.get_num_layers()):
            worksheet.write(i+k, 0, 'Layer ' + str(k+1))

        l, ls, lcol = data.get_layers()
        for k1 in range(np.shape(l)[0]):
            for k2 in range(np.shape(l)[1]):
                cell_format = workbook.add_format({'bg_color': lcol[k1,k2], 'align': 'center'})
                worksheet.write(k1+2, k2+1, ls[k1,k2], cell_format)

        worksheet.set_column(0, 0 , width = 15)
        worksheet.set_column(1, data.machinedata['Q'] , width = 4.5)
        i += data.get_num_layers()
        i += 2
        
        
        if type(data.machinedata['turns']) == type([]):
            cell_format = workbook.add_format({'font_size': 14})
            worksheet.write(i, 0, 'Number of turns', cell_format)
            i += 1
            for k in range(data.get_num_layers()):
                worksheet.write(i+k, 0, 'Layer ' + str(k+1))
            
            turns = data.machinedata['turns']
            for km, ph in enumerate(data.machinedata['phases']):
                col = get_phase_color(km)
                cell_format = workbook.add_format({'bg_color': col, 'align': 'center'})
                for kl in range(len(ph)):
                    layer = ph[kl]
                    for j,cs in enumerate(layer):
                        if type(turns) == type([]):
                            item = turns[km][kl][j]
                        else:
                            item = turns
                        if cs > 0:
                            worksheet.write(i+kl, 1+cs-1, item, cell_format)
                        else:
                            worksheet.write(i+kl, 1+abs(cs)-1, item, cell_format)
              
            i += data.get_num_layers()
        else:
            worksheet.write(i, 0, 'Number of turns')
            worksheet.write(i, 1, data.machinedata['turns'])
        i += 2
        
        cell_format = workbook.add_format({'font_size': 14})
        worksheet.write(i, 0, 'slot number per phase', cell_format)
        i += 1
        for kph, ph in enumerate(data.machinedata['phases']):
            for klay,lay in enumerate(ph):
                worksheet.write(i, 0, 'Phase '+str(kph+1)+' layer '+str(klay+1))
                cell_format = workbook.add_format({'align': 'center'})
                worksheet.write_row(i, 1, lay, cell_format)
                i += 1


    if phasors:
        worksheet = workbook.add_worksheet('phasors')

        cell_format = workbook.add_format({'font_size': 14})
        worksheet.write(0, 0, 'Voltage phasors', cell_format)
        max_i = 0
        for knu in range(len(data.results['Ei_el'])):
            i = max_i+2
            worksheet.write(i, 0, 'nu = '+str(data.results['nu_el'][knu]))
            i += 1
            dx = 0
            
            for m,phasors in enumerate(data.results['Ei_el'][knu]):
                worksheet.write(i, dx+0, 'Phase'+str(m+1)+'_real')
                worksheet.write(i, dx+1, 'Phase'+str(m+1)+'_imag')
                for k in range(len(phasors)):
                    worksheet.write(i+1, dx, phasors[k].real)
                    worksheet.write(i+1, dx+1, phasors[k].imag)
                    i += 1
                max_i = i if i > max_i else max_i
                i -= len(phasors)   # go back for new columns
                dx += 2
                    
    if windingfactor_el:
        worksheet = workbook.add_worksheet('Winding_factor_el)')
        cell_format = workbook.add_format({'font_size': 14})
        worksheet.write(0, 0, 'Winding factor (electrical)', cell_format)
        
        worksheet.write(2, 0, 'nu')
        for km in range(data.get_num_phases()):
            worksheet.write(2, km+1, 'phase'+str(km+1))

        nu, kw = data.get_windingfactor_el()
        worksheet.write_column(3, 0, nu)
        for km in range(data.get_num_phases()):
            worksheet.write_column(3, km+1, kw[:,km])


    if windingfactor_mech:
        worksheet = workbook.add_worksheet('Winding_factor_mech)')
        cell_format = workbook.add_format({'font_size': 14})
        worksheet.write(0, 0, 'Winding factor (mechanical)', cell_format)
        
        worksheet.write(2, 0, 'nu')
        for km in range(data.get_num_phases()):
            worksheet.write(2, km+1, 'phase'+str(km+1))

        nu, kw = data.get_windingfactor_mech()
        worksheet.write_column(3, 0, nu)
        for km in range(data.get_num_phases()):
            worksheet.write_column(3, km+1, kw[:,km])

    workbook.close()


class TextReport:
    def __init__(self, data):
        """
        Class for creating Text reports of the winding

        Parameters
        ----------
        data :   datamodel object
                 winding model for creating the report
        """  
        self.data = data
        self._txt = []
        
    def create(self):
        self._txt.append('TITLE')
        self._txt.append('=====')
        self._txt.append(self.data.get_title())
        self._txt.append('\n')
        
        self._txt.append('NOTES')
        self._txt.append('=====')
        self._txt.append(self.data.get_notes())
        self._txt.append('\n')
        
        self._txt.append('MACHINE DATA')
        self._txt.append('============')
        self._txt.append('Number of slots        Q: {}'.format(self.data.get_num_slots()))
        self._txt.append('Number of pole pairs   p: {}'.format(self.data.get_num_polepairs()))
        self._txt.append('Number of phases       m: {}'.format(self.data.get_num_phases()))
        self._txt.append('Number of slots/phase  q: {}'.format(self.data.get_q()))
        self._txt.append('\n')
        
        _, ls, _ = self.data.get_layers()
        self._txt.append('WINDING LAYOUT')
        self._txt.append('==============')
        self._txt.append('Layer_1: ' + ' | '.join([k for k in ls[0,:]]))
        if self.data.get_num_layers() > 1:
            self._txt.append('Layer_2: ' + ' | '.join([k for k in ls[1,:]]))
        
        self._txt.append('\n')
        
        
        bc, txt = self.data.get_basic_characteristics()
        self._txt.append('ANALYSIS')
        self._txt.append('========')
        self._txt.append('Periodic base winding                  t: {}'.format(bc['t']))
        a_ = [str(i) for i in analyse.Divisors(bc['a'])]
        self._txt.append('Possible parallel winding connections  a: {}'.format(', '.join(a_)))
        
        for k in range(len(bc['kw1'])):
            self._txt.append('Fundamental winding factor           kw1: {} (phase{})'.format(round(bc['kw1'][k], 3), k+1))
        self._txt.append('Double linked leakage            sigma_d: {} (from MMF)'.format(round(bc['sigma_d'], 3)) )
        self._txt.append('\n')
        
        self._txt.append('Harmonic content of the winding faktor (electrical)')
        self._txt.append('nu_el\t' + '\t'.join(['kw ('+k+')' for k in self.data.get_phasenames()]))
        nu, kw = self.data.get_windingfactor_el()

        for knu in range(len(nu)):
            kw_ = [num2str(k, 8) for k in kw[knu]]
            self._txt.append( str(nu[knu])+'\t'+ '\t'.join(kw_) )
        self._txt.append('\n')
        
        self._txt.append('Harmonic content of the winding faktor (mechanical)')
        self._txt.append('nu_mech\t' + '\t'.join(['kw ('+k+')' for k in self.data.get_phasenames()]))
        nu, kw = self.data.get_windingfactor_mech()

        for knu in range(len(nu)):
            kw_ = [num2str(k, 8) for k in kw[knu]]
            self._txt.append( str(nu[knu])+'\t'+ '\t'.join(kw_) )
        self._txt.append('\n')
        
        
        self._txt.append('FORCES')
        self._txt.append('======')
        self._txt.append('Cogging torque ordinal numbers for pm-machines: {}, {}, {}, ...'.format(bc['lcmQP'], bc['lcmQP']*2, bc['lcmQP']*3))
        r_ = [str(i) for i in bc['r']]
        self._txt.append('The winding leads to radial forces with modes r: {}, ...'.format(', '.join(r_)))

        #  self._txt.append()

        #  self._txt.append()
        #  self._txt.append()
        
        
    def get_report(self):
        if len(self._txt) == 0:
            self.create()
        return '\n'.join(self._txt)
        
        
    def save(self, fname):
        with open(fname, 'w') as f:
            f.write(self.get_report())





