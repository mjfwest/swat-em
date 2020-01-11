# -*- coding: utf-8 -*-
'''
Provides functions for plotting
''' 

from PyQt5.QtWidgets import QTableWidgetItem, QApplication
from PyQt5.QtGui import QFont
from PyQt5 import QtCore
from swat_em.config import get_phase_color, get_line_color, config
from swat_em import analyse

import numpy as np
import time
import os

# WORKAROUND for pyqtgraph's printing system
#  from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
#  import PyQt5.QtGui
#  PyQt5.QtGui.QPrinter = QPrinter
#  PyQt5.QtGui.QPrintDialog = QPrintDialog

import pyqtgraph as pg
import pyqtgraph.exporters
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOptions(antialias=True)


class _slot_plot:
    sh = 0.8  # slot height
    sw = 0.75  # slot width
    so = 0.2  # slot opening

    def __init__(self, layout, widget, data):
        self.layout = layout
        self.widget = widget
        self.data = data
        self.Q = 0
        self.slot = {}
        self.devide = 'h'  # slot devide h (horizontal) or v (vertical

        if self.layout is None:
            self.app = pg.mkQApp()
            self.fig = pg.PlotWidget() #title='xyz'
        else:
            self.fig = pg.PlotWidget()
            self.layout.addWidget(self.fig)
        self.fig.setAspectLocked(lock=True, ratio=1)
        self.fig.getAxis('bottom').hide()
        self.fig.getAxis('left').hide()
       
    
    def plot_slots(self, Q):
        if Q <= 0:
            return False
        sh = self.sh  # slot height
        sw = self.sw  # slot width
        so = self.so  # slot opening

        self.fig.clear()
        self.fig.disableAutoRange()    # disable because of porformance 
                                       # (a lot of elements are plottet)
        
        x = [0]*10
        y = [0]*10
        x[0], y[0] = 0.0, 1.0
        x[1], y[1] = 0.5 - so/2, 1.0
        x[2], y[2] = 0.5 - so/2, sh
        x[3], y[3] = 0.5 - sw/2, sh
        x[4], y[4] = 0.5 - sw/2, 0.0
        x[5], y[5] = 0.5 + sw/2, 0.0
        x[6], y[6] = 0.5 + sw/2, sh
        x[7], y[7] = 0.5 + so/2, sh
        x[8], y[8] = 0.5 + so/2, 1.0
        x[9], y[9] = 1.0, 1.0

        xp = [[]]
        yp = [[]]
        i_slots = 0
        dx = 0
        dy = 0
        for k in range(Q):
            if i_slots >= 12:
                dx = 0
                dy += -1.5
                i_slots = 0
                xp.append([])
                yp.append([])
            for a, b in zip(x,y):
                xp[-1].append(a+dx)
                yp[-1].append(b+dy) 
            dx += 1
            i_slots += 1
        for k in range(len(xp)):
            pen = pg.mkPen(color='k', width = 1.5)  
            curve = pg.PlotCurveItem(xp[k], yp[k], pen=pen)
            self.fig.addItem(curve)
        
        i_slots = 0
        dy = 0
        dx = 0
        for k in range(Q):
            if i_slots >= 12:
                dx = 0
                dy += -1.5
                i_slots = 0

            txt = pg.TextItem(str(k+1), anchor=(0.5,0.5))
            txt.setPos(0.5+dx, -0.3+dy)
            txt.setColor('k')
            self.fig.addItem(txt, ignoreBounds=True) # ignore because autoRange have problems with it
                
            dx += 1
            i_slots += 1
        #  self.fig.autoRange()
        self.fig.setXRange(0, 12)
        self.fig.autoRange()
        
                        
    def plot(self, data, show = False):
        self.data = data
        self.show = show
        S = self.data.get_phases()
        Q = self.data.get_num_slots()
        self.devide = 'v' if self.data.get_windingstep() == 1 else 'h'

        def add_text(slot, phase, pos, wdir):
            dx = slot
            dy = self.sh / 2
            while dx > 12:
                dx -= 12
                dy -= 1.5
            dx = dx -1 + 0.5

            if self.devide == 'h':
                if pos == 0:         # bottom layer
                    dy -= self.sh/4
                elif pos == 1:       # top layer
                    dy += self.sh/4
                    
            elif self.devide == 'v':
                if pos == 0:         # right layer
                    dx += self.sw/4
                elif pos == 1:       # left layer
                    dx -= self.sw/4
            
            if wdir > 0:
                txt = '+' + str(phase)  # '$\otimes$'
            else:
                txt = '-' + str(phase)  # '$\odot$'

            text = pg.TextItem(anchor=(0.5,0.5))
            text.setHtml('<div><b>'+txt+'</b></div>')
            #  text.setPlainText(txt)
            text.setPos(dx, dy)
            text.setColor(get_phase_color(phase-1))
            self.fig.addItem(text, ignoreBounds=True) # ignore because autoRange have problems with it
        

        for m, phase in enumerate(S):
            pos = 0
            for layer in phase:
                for cs in layer:
                    add_text(abs(cs), m+1, pos, cs)
                pos += 1
        self.fig.autoRange()
        if self.show:
            self.fig.show()
            self.app.exec_()
                
    def save(self, fname, res):
        if self.show:
            self.app.processEvents()
        if os.path.splitext(fname)[-1].upper() == '.SVG':
            exporter = pg.exporters.SVGExporter(self.fig.plotItem)
        else:
            exporter = pg.exporters.ImageExporter(self.fig.plotItem)
            exporter.params.param('width').setValue(int(res[0]), blockSignal=exporter.widthChanged)
            exporter.params.param('height').setValue(int(res[1]), blockSignal=exporter.heightChanged)
        exporter.export(fname)
    
    
    #  def printing(self):
        #  exporter = pg.exporters.PrintExporter(self.fig.plotItem)
        #  exporter.export()





class _slot_star:

    def __init__(self, layout, widget, data, table):
        self.layout = layout
        self.widget = widget
        self.data = data
        self.table = table

        if self.layout is None:
            self.app = pg.mkQApp()
            self.fig = pg.PlotWidget() #title='xyz'
        else:
            self.fig = pg.PlotWidget()
            self.layout.addWidget(self.fig)
        self.fig.getAxis('bottom').hide()
        self.fig.getAxis('left').hide()
        self.fig.setAspectLocked(lock=True, ratio=1)
        self.leg = self.fig.addLegend(offset=(-10, 10))

        
    
    def plot(self, data, harmonic_idx = 0, ForceX = None, show = False):
        self.data = data
        self.show = show
        if harmonic_idx < 0:
            harmonic_idx = 0

        self.fig.clear()
        try:
            self.leg.scene().removeItem(self.leg)
        except Exception as e:
            print(e)
        self.leg = self.fig.addLegend(offset=(-10, 10))
        self.fig.disableAutoRange()# disable because of porformance 
                                   # (a lot of elements are plottet)
        
        xlim = [0, 0] # find limit manually, because autoscale doesn't work with plt.arrow()
        ylim = [0, 0]
        def plot_vek(vek, color='k', dangle = None, idx=None):
            '''
            vek: list of complex values
            dangle: All phasors get shifted by dangle
            '''
            if dangle is not None:
                A = np.abs(vek)
                ph = np.angle(vek)
                ph -= dangle
                vek = A*np.exp(1j*ph)
                
            old = 0+0j
            v = np.cumsum(vek)

            for k in range(len(vek)): # find limit manually, because autoscale doesn't work with plt.arrow()
                if min(v.real) < xlim[0]:
                    xlim[0] = min(v.real)
                if max(v.real) > xlim[1]:
                    xlim[1] = max(v.real)
                if min(v.imag) < ylim[0]:
                    ylim[0] = min(v.imag)
                if max(v.imag) > ylim[1]:
                    ylim[1] = max(v.imag)
                
                arrow = pg.ArrowItem(angle=180-np.angle(vek[k])/np.pi*180, headLen=12, pen={'color': color}, brush=color)
                arrow.setPos(old.real+vek[k].real, old.imag+vek[k].imag)
                self.fig.addItem(arrow)
                line = pg.PlotCurveItem([old.real, vek[k].real+old.real], [old.imag, vek[k].imag+old.imag], 
                    pen={'color': color, 'width': config['plt']['lw']})
                self.fig.addItem(line)
            
                old = v[k]
            line = pg.PlotCurveItem([0.0, v[-1].real], [0.0, v[-1].imag], name = 'Phase '+str(idx+1),
                    pen={'color': color, 'width': config['plt']['lw'], 'style': pg.QtCore.Qt.DashLine})
            self.fig.addItem(line)

        if ForceX:
            angle_phase1 = np.angle(np.sum(self.data.results['Ei_el'][harmonic_idx][0]))
        else:
            angle_phase1 = None
        for k in range(len(self.data.results['Ei_el'][harmonic_idx])):
            plot_vek(self.data.results['Ei_el'][harmonic_idx][k], color = get_phase_color(k), dangle = angle_phase1, idx=k)

        self.fig.autoRange()
        if show:
            self.fig.show()
            self.app.exec_()
                

        # update table:        
        ei = self.data.results['Ei_el'][harmonic_idx]        
        
        if self.table is not None:
            self.table.setRowCount(len(ei))
            self.table.setColumnCount(3)
            
            for km in range(len(ei)):
                A = np.abs( np.sum(ei[km]) )
                ph = np.angle( np.sum(ei[km]) )/np.pi*180
                self.table.setItem(km, 0, QTableWidgetItem(str(km+1)))
                self.table.setItem(km, 1, QTableWidgetItem(str(round(A,1))))
                self.table.setItem(km, 2, QTableWidgetItem(str(round(ph,1))))
                
                for i in range(3): # set all cells as not editable
                    self.table.item(km, i).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

            for k1 in range(len(ei)):
                self.table.resizeColumnToContents(k1)


            self.table.setHorizontalHeaderLabels(['m', 'A', 'phase'])
            #  self.table.setVerticalHeaderLabels(['']*np.shape(kw)[0])
            afont = QFont()
            afont.setBold(True)
            
            for k in range(3):
                self.table.horizontalHeaderItem(k).setFont(afont)


    def save(self, fname, res):
        if self.show:
            self.app.processEvents()
        if os.path.splitext(fname)[-1].upper() == '.SVG':
            exporter = pg.exporters.SVGExporter(self.fig.plotItem)
        else:
            exporter = pg.exporters.ImageExporter(self.fig.plotItem)
            exporter.params.param('width').setValue(int(res[0]), blockSignal=exporter.widthChanged)
            exporter.params.param('height').setValue(int(res[1]), blockSignal=exporter.heightChanged)
        exporter.export(fname)


    #  def printing(self):
        #  exporter = pg.exporters.PrintExporter(self.fig.plotItem)
        #  exporter.export()


class _windingfactor:
    def __init__(self, layout, widget, data, table):
        self.layout = layout
        self.widget = widget
        self.data = data
        self.table = table

        if self.layout is None:
            self.app = pg.mkQApp()
            self.fig = pg.PlotWidget() #title='xyz'
        else:
            self.fig = pg.PlotWidget()
            self.layout.addWidget(self.fig)
        self.fig.setLabel('bottom', '<div>ordinal number &nu;</div>')
        self.fig.setLabel('left', '<div>Windingfactor kw</div>') #<div>Windingfactor &xi;</div>
        self.fig.showGrid(x=True, y=True)
        self.leg = self.fig.addLegend(offset=(-10, 10))
        self.fig.setLimits(xMin = 0, yMin = 0)
        
        
    
    def plot(self, data, mechanical = False, show = False):
        self.data = data
        self.show = show
        self.fig.clear()
        try:
            self.leg.scene().removeItem(self.leg)
        except Exception as e:
            print(e)
        self.leg = self.fig.addLegend(offset=(-10, 10))
        
        if mechanical:
            nu = np.array(self.data.results['nu_mech'])
            kw = np.array(self.data.results['kw_mech'])
        else:
            nu = np.array(self.data.results['nu_el'])
            kw = np.array(self.data.results['kw_el'])
        
        #  gap = 0.2
        N = np.shape(kw)[1]
        for k in range(N):
            dx = nu[1] - nu[0]
            x = nu - dx/N/1.5 + dx/N/1.5*k

            pen = pg.mkPen(width = 0., color=get_phase_color(k))  
            bar = pg.BarGraphItem(x=x, height=np.abs(kw[:,k]), width=(dx)/1.5/N, 
                    brush=get_phase_color(k), pen=pen) # , name='Phase '+str(k+1)
            self.fig.addItem(bar)
            
            # workaround: Plot points for legend because 'BarGraphItem' has no 'name'
            line = pg.PlotCurveItem(x, np.abs(kw[:,k]), '.', name='Phase '+str(k+1), pen=pen)
            self.fig.addItem(line)

        if show:
            self.fig.show()
            self.app.exec_()

        
        
        if self.table is not None:
            # update table:
            self.table.setRowCount(np.shape(kw)[0])
            self.table.setColumnCount(N+1)
            
            for k1 in range(np.shape(kw)[0]):
                self.table.setItem(k1, 0, QTableWidgetItem(str(nu[k1])))
                for k2 in range(np.shape(kw)[1]):
                    self.table.setItem(k1, k2+1, QTableWidgetItem(str(round(kw[k1,k2],3))))
                    # set all cells as not editable
                    self.table.item(k1, k2+1).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            for k1 in range(np.shape(kw)[0]):
                self.table.resizeColumnToContents(k1)


            self.table.setHorizontalHeaderLabels(['nu'] + self.data.get_phasenames())
            self.table.setVerticalHeaderLabels(['']*np.shape(kw)[0])
            afont = QFont()
            afont.setBold(True)
            
            for k in range(self.data.get_num_phases() + 1):
                self.table.horizontalHeaderItem(k).setFont(afont)

    def save(self, fname, res):
        if self.show:
            self.app.processEvents()
        if os.path.splitext(fname)[-1].upper() == '.SVG':
            exporter = pg.exporters.SVGExporter(self.fig.plotItem)
        else:
            exporter = pg.exporters.ImageExporter(self.fig.plotItem)
            exporter.params.param('width').setValue(int(res[0]), blockSignal=exporter.widthChanged)
            exporter.params.param('height').setValue(int(res[1]), blockSignal=exporter.heightChanged)
        exporter.export(fname)


    #  def printing(self):
        #  exporter = pg.exporters.PrintExporter(self.fig.plotItem)
        #  exporter.export()


class _mmk:
    def __init__(self, layout, widget, data, table):
        self.layout = layout
        self.widget = widget
        self.data = data
        self.table = table

        if self.layout is None:
            self.app = pg.mkQApp()
            
        self.l = pg.GraphicsLayoutWidget()
        self.fig1 = self.l.addPlot(row=1, col=1, rowspan=1)
        self.fig2 = self.l.addPlot(row=2, col=1, rowspan=1)
        if self.layout is not None:
            self.layout.addWidget(self.l)
        
        self.fig1.setLabel('bottom', 'circumferential stator slots')
        self.fig1.setLabel('left', 'MMF in A')
        self.fig1.showGrid(x=True, y=True)
        self.leg1 = self.fig1.addLegend(offset=(-10, 10))
        
        self.fig2.setLabel('bottom', 'circumferential stator slots')
        self.fig2.setLabel('left', 'Current in slot in A')
        self.fig2.showGrid(x=True, y=True)
        
        
    def plot(self, data, phase = 0, small_update = False, show = False):
        '''
        Plottet MMF-Kurve

        Parameters
        ----------
        plot_MMK_nu :           iterable - list/tuple
                                Liste/Tuple mit Ordnungszahlen, die geplottet werden sollen
        plot_MMK_greater_than : scalar, float
                                Plotte alle Oberschwingungen mit der Amplitude größer als
        '''
        self.data = data
        self.show = show
        plot_MMK_greater_than = config['plot_MMF_harmonics']

        #  MMK =  self.data.results['MMK']['MMK']
        #  phi = np.array(self.data.results['MMK']['phi'])
        #  theta = self.data.results['MMK']['theta'] 
        phi, MMK, theta = analyse.calc_MMK(self.data.get_num_slots(),
                                   self.data.get_num_phases(),
                                   self.data.get_phases(),
                                   self.data.get_turns(),
                                   angle = phase)          
        phi = np.array(phi)
        nu = np.array(self.data.results['MMK']['nu'])
        HA = analyse.DFT(MMK[:-1])[:len(nu)]
        A = np.abs(HA)
        phase = np.angle(HA)

        self.fig1.clear()
        self.fig1.disableAutoRange()# disable because of porformance 
                                    # (a lot of elements are plottet)
        try:
            self.leg1.scene().removeItem(self.leg1)
        except Exception as e:
            print(e)
        self.leg1 = self.fig1.addLegend(offset=(-10, 10))
        pen = pg.mkPen(color=get_line_color(0), width = config['plt']['lw'])  
        curve = pg.PlotCurveItem(phi, MMK, pen=pen)
        self.fig1.addItem(curve)
       
        
        # Plotte Oberschwingungen
        i = 1
        for n, a, p in zip(nu, A, phase):
            if 1/max(A)*a > plot_MMK_greater_than:
                pen = pg.mkPen(color=get_line_color(i), width = config['plt']['lw_thin']) 
                curve = pg.PlotCurveItem(phi, a*np.cos(n*phi/phi[-1]*2*np.pi + p), name='<div>&nu;={}</div>'.format(n), pen=pen)
                self.fig1.addItem(curve)
                i += 1
        self.fig1.autoRange()
        self.fig1.setLimits(xMin = min(phi), xMax = max(phi))

        self.fig2.clear()
        pen = pg.mkPen(width = 0., color=get_line_color(0))  
        bar = pg.BarGraphItem(x=range(len(theta)), height=theta, width = 0.5, 
                brush=get_line_color(0), pen=pen) # , name='Phase '+str(k+1)
        self.fig2.addItem(bar)
        self.fig2.setXRange(min(phi), max(phi))
        if show:
            self.l.show()
            self.app.exec_()


        if self.table is not None:
            # update table:
            self.table.setRowCount(len(A)-1)
            self.table.setColumnCount(3)
            self.table.setHorizontalHeaderLabels(['nu', 'Amp', '[%]'])
            
            for k1 in range(1, len(A)):
                self.table.setItem(k1-1, 0, QTableWidgetItem(str(nu[k1])))
                a = A[k1]
                a_rel = 100.0/max(A)*a
                self.table.setItem(k1-1, 1, QTableWidgetItem(str(round(a, 3))))
                self.table.setItem(k1-1, 2, QTableWidgetItem(str(round(a_rel, 1))))
                for i in range(3): # set all cells as not editable
                    self.table.item(k1-1, i).setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            for k1 in range(3):
                self.table.resizeColumnToContents(k1)

    def save(self, fname, res):
        self.app.processEvents()
        
        if os.path.splitext(fname)[-1].upper() == '.SVG':
            exporter = pg.exporters.SVGExporter(self.l.ci)
        else:
            exporter = pg.exporters.ImageExporter(self.l.ci)
            exporter.params.param('width').setValue(int(res[0]), blockSignal=exporter.widthChanged)
            exporter.params.param('height').setValue(int(res[1]), blockSignal=exporter.heightChanged)
        exporter.export(fname)


    #  def printing(self):
        #  exporter = pg.exporters.PrintExporter(self.l.ci)
        #  exporter.export()
