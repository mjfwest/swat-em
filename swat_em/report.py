# -*- coding: utf-8 -*-
'''
Provides functions for reports
''' 
import os
import tempfile
import numpy as np
from swat_em import analyse

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


class HtmlReport:
    def __init__(self, data):
        self.data = data
        self.template = os.path.abspath(os.path.join(os.path.dirname(__file__), 'template', 'report.html'))


    def create_figures(self, tmpdir):
        self.data.plot_layout(os.path.join(tmpdir,'plot_layout.png'), res = [800, 600])
        self.data.plot_star(os.path.join(tmpdir,'plot_star.png'), res = [800, 600])
        self.data.plot_windingfactor(os.path.join(tmpdir,'plot_wf_el.png'), mechanical = False, res = [800, 600])
        self.data.plot_windingfactor(os.path.join(tmpdir,'plot_wf_mech.png'), mechanical = True, res = [800, 600])
        self.data.plot_MMK(os.path.join(tmpdir,'plot_MMK.png'), res = [800, 600], phase = 0)

    def create(self):
        #  tmpdir = tempfile.mkdtemp()
        
        filename = '/media/ramdisk/report.html'
        tmpdir = '/media/ramdisk'   # for testing
        
        
        self.create_figures(tmpdir)
        
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

        
        
        
        with open(self.template) as f:
            tmpl = f.readlines()
        
        _report = []
        for line in tmpl:
            line = line.strip()
            line = line.replace('{{ TITLE }}', self.data.get_title())
            line = line.replace('{{ NOTES }}', self.data.get_notes())
            
            line = line.replace('{{ plot_layout }}', os.path.join(tmpdir, 'plot_layout.png'))
            txt, html = self.data.get_basic_characteristics()
            line = line.replace('{{ table_bc }}', html)
            
            line = line.replace('{{ plot_star }}', os.path.join(tmpdir, 'plot_star.png'))
            line = line.replace('{{ table_star }}', _table_star)
            line = line.replace('{{ plot_wf_el }}', os.path.join(tmpdir, 'plot_wf_el.png'))
            line = line.replace('{{ table_wf_el }}', _table_wf_el)
            line = line.replace('{{ plot_wf_mech }}', os.path.join(tmpdir, 'plot_wf_mech.png'))
            line = line.replace('{{ table_wf_mech }}', _table_wf_mech)
            line = line.replace('{{ plot_MMK }}', os.path.join(tmpdir, 'plot_MMK.png'))
            line = line.replace('{{ table_MMK }}', _table_wf_mech)
            
            _report.append(line)
        
        
        with open(filename, 'w') as f:
            f.write('\n'.join(_report))

        import webbrowser
        webbrowser.open(filename)






