# -*- coding: utf-8 -*-
'''
Provides functions for plotting
''' 

from PyQt5.QtWidgets import QTableWidgetItem, QApplication
from PyQt5.QtGui import QFont, QSyntaxHighlighter, QTextCursor,\
                        QTextCharFormat, QColor
from PyQt5 import QtCore




from swat_em.config import get_phase_color, get_line_color, config
from swat_em import analyse

import numpy as np
import time
import os
import re

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



def create_wdg_overhang(S, Q, num_layers, w = None, optimize_wdg_overhang = False):
    '''
    Generate the winding overhang (connection of the coil sides).

    Parameters
    ----------
    S :                     list of lists
                            winding layout
    Q :                     integer
                            number of slots
    num_layers :            integer
                            number winding layers
    w :                     integer or list of integers
                            winding step(s)
                 
    optimize_wdg_overhang : Boolean
                            number of phases
             
    Returns
    -------
    return : list 
             Winding connections for all phases, len = num_phases,
             format: [[(from_slot, to_slot, stepwidth, direction), ()], [(), ()], ...]
             from_slot: slot with positive coil side of the coil
             to_slot:   slot with negative coil side of the coil
             stepwidth: distance between from_slot to to_slot
             direction: winding direction (1: from left to right, -1: from right to left)
    '''
    if w is not None:
        if not hasattr(w, '__iter__'):
            w = [int(w)]     # int() because w could be Fractional.fraction()
 
        
    head = []
    for ph_ in S:
        head.append([])

        ph = analyse._flatten([ph_])[0]
        pos = []
        neg = []
        for p in ph:
            if p>0:
                pos.append(p)
            else:
                neg.append(-p)
        if len(pos) != len(neg):
            raise Exception('Number of positive and negative coils sides must be equal')

        for kpos in range(len(pos)):
            
            diff = []
            direct_ = []
            for kneg in range(len(neg)):
                diff1 = abs(pos[kpos] - neg[kneg])
                diff2 = abs( abs(pos[kpos] - neg[kneg]) -Q )
                diff_tmp = diff1 if diff1<diff2 else diff2
                diff.append(diff_tmp)
            
            if w is None or optimize_wdg_overhang:
                index_min = min(range(len(diff)), key=diff.__getitem__)
            else:
                for w_ in w:
                    if w_ in diff:
                        index_min = diff.index(w_)
                        break
            if neg[index_min] - pos[kpos] == diff[index_min]: # forward, no overflow
                direct = 1
            elif neg[index_min] - pos[kpos] + Q == diff[index_min]: # forward, no overflow
                direct = 1
            else:
                direct = -1

            head[-1].append((pos[kpos], neg.pop(index_min), diff[index_min], direct))
    return head


def gen_coil_lines(w, h1 = 0.75, h2 = 1.5, db1 = 0.1, Np1 = 21):
    '''
    Create lines of a coil for plotting.

    Parameters
    ----------
    w :  integer
         width of the coil in slots
    h1:  float
         height of the coil side in the slot
    h2:  float
         max height of the winding overhang
    db1: float
         distance of the coil side to the middle of the slot;
         should be 0..0.2
    Np1: integer
         number of plotting points in the line of the winding overhang

    Returns
    -------
    x : list 
        x values of the coil for plotting
    y : list
        y values of the coil for plotting
    '''
    x1, y1 = db1, h1
    x2, y2 = w/2, h2
    x3, y3 = w-db1, h1
    x4, y4 = x3, -y3
    x5, y5 = x2, -x2
    x6, y6 = x1, -y1

    x = []
    y = []
    x_ = np.linspace(x1, x3, Np1)
    y_ = np.interp(x_, [x1,x2,x4], [y1,y2,y3])
    x += x_.tolist()
    y += y_.tolist()

    x += x_[::-1].tolist()
    y += (-1*y_[::-1]).tolist()
    x.append(x[0])
    y.append(y[0])
    return x, y


def gen_slot_lines(Q, bz, hz):
    '''
    Create lines of a slot for plotting.

    Parameters
    ----------
    q :  integer
         number of slots
    bz:  float
         width of the tooth -> Slot width = 1 - bz
         so bz should be around 0.5
    hz:  float
         height of the slots

    Returns
    -------
    x : list 
        x values of the slots for plotting
    y : list
        y values of the slots for plotting
    '''
    x = []
    y = []
    for k in range(Q+1):
        x1 = k-0.5
        if k == 0:
            x += [x1, x1, x1+bz/2, x1+bz/2, x1, np.nan]
        elif k == Q:
            x += [x1-bz/2, x1-bz/2, x1, x1, x1-bz/2, np.nan]
        else:
            x += [x1-bz/2, x1-bz/2, x1+bz/2, x1+bz/2, x1-bz/2, np.nan]
        y += [-hz, hz, hz, -hz, -hz, np.nan]
    return x, y


def gen_slot_filling(Q, bz, hz):
    '''
    Create lines of a slot for plotting.

    Parameters
    ----------
    q :  integer
         number of slots
    bz:  float
         width of the tooth -> Slot width = 1 - bz
         so bz should be around 0.5
    hz:  float
         height of the slots

    Returns
    -------
    x : list 
        x values of the slots for plotting
    y : list
        y values (upper lines) of the slots for plotting
    y_neg : list
        y values (lower lines) of the slots for plotting
    '''
    x = []
    y = []
    for k in range(Q+1):
        x1 = k-0.5
        if k == 0:
            x += [x1, x1+bz/2, np.nan]
        elif k == Q:
            x += [x1+bz/2, x1+bz/2, np.nan]
        else:
            x += [x1-bz/2, x1+bz/2, np.nan]
        y += [hz, hz, np.nan]
    y_neg = [-k for k in y]
    return x, y, y_neg



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


class _overhang_plot:
    bz = 0.5  # tooth width
    hz = 0.5  # slot height
    h1 = 0.6  # height of the coil side
    #  h2 = 1.5  # height of the winding overhang
    db1 = 0.1 # distance between coil side and slot center
    Np1 = 101  # number of plotting points in the winding overhang per coil


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
        #  self.fig.setAspectLocked(lock=True, ratio=1)
        self.fig.getAxis('bottom').hide()
        self.fig.getAxis('left').hide()
       
    
    def plot(self, data = None, show = False, optimize_overhang = False):
        self.show = show
        if data is not None:
            self.data = data
        
        S = self.data.get_phases()
        Q = self.data.get_num_slots()
        w = self.data.get_windingstep()
        num_layers = self.data.get_num_layers()
        
        self.fig.clear()
        try:
            self.leg.scene().removeItem(self.leg)
        except Exception as e:
            #  print(e)
            pass
        self.leg = self.fig.addLegend(offset=(-10, 10))
        
        self.fig.disableAutoRange()# disable because of porformance 
                                   # (a lot of elements are plottet)
        
        # plot slots - lines
        #  x, y = gen_slot_lines(Q, bz = self.bz, hz = self.hz)
        #  pen = pg.mkPen(color='#808080', width = 1.5)  
        #  curve = pg.PlotCurveItem(x, y, pen=pen, connect='finite')
        #  self.fig.addItem(curve)
        
        # plot slots - filling
        brush = pg.mkBrush(color='#BFBFBF')
        x, y_upper, y_lower = gen_slot_filling(Q, bz = self.bz, hz = self.hz)
        c1 = pg.PlotCurveItem(x, y_upper, connect='finite')
        c2 = pg.PlotCurveItem(x, y_lower, connect='finite')
        fill = pg.FillBetweenItem(c1, c2, brush = brush)
        self.fig.addItem(fill)

        
        # plot coils
        try:  # TODO: Experimental
            head = create_wdg_overhang(S, Q, num_layers, w = w, optimize_wdg_overhang = optimize_overhang)
        except:
            head = []
        i = 1
        for phase in head:
            x = []
            y = []
            for coil in phase:
                w = coil[2]
                x_, y_ = gen_coil_lines(coil[2], h1 = self.h1, h2=0.5+w/6, db1=self.db1, Np1=self.Np1)
                x_, y_ = np.array(x_), np.array(y_)
                
                direct = coil[3]
                if direct > 0:
                    x_ += coil[0] - 1
                else:
                    x_ += coil[1] - 1

                # split coil on right border
                x_2 = x_.copy()
                y_2 = y_.copy()
                x_2[x_<Q-0.5] = np.nan
                x_2 -= Q
                y_2[x_<Q-0.5] = np.nan
                y_[x_>Q-0.5] = np.nan
                x_[x_>Q-0.5] = np.nan
                x += x_.tolist()
                y += y_.tolist()
                x += [np.nan]
                y += [np.nan]
                x += x_2.tolist()
                y += y_2.tolist()
                x += [np.nan]
                y += [np.nan]
                
                # plot arrows (winding direction)
                arrow = pg.ArrowItem(angle=90, headLen=16, pen={'color': get_phase_color(i-1)}, brush=get_phase_color(i-1))
                if coil[3] > 0:
                    arrow.setPos(coil[0]-1+self.db1, 0)
                else:
                    arrow.setPos(coil[0]-1-self.db1, 0)
                self.fig.addItem(arrow)
                
                arrow = pg.ArrowItem(angle=-90, headLen=16, pen={'color': get_phase_color(i-1)}, brush=get_phase_color(i-1))
                if coil[3] > 0:
                    arrow.setPos(coil[1]-1-self.db1, 0)
                else:
                    arrow.setPos(coil[1]-1+self.db1, 0)
                self.fig.addItem(arrow)
                
            pen = pg.mkPen(color = get_phase_color(i-1), width = config['plt']['lw'])  
            curve = pg.PlotCurveItem(x, y, pen=pen, connect='finite', name = 'Phase '+str(i))
            self.fig.addItem(curve)
            i += 1

        # plot slot number
        for k in range(Q):
            text = pg.TextItem(anchor=(0.5,0.5))
            text.setPlainText(str(k+1))
            text.setPos(k, -self.h1/2)
            text.setColor('k')
            self.fig.addItem(text, ignoreBounds=True) # ignore because autoRange have problems with it


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
        if self.show:
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


class _Report_Highlighter(QSyntaxHighlighter):
    '''
    Syntax highlighting for report
    '''
    def __init__(self, parent=None):
        super(_Report_Highlighter, self).__init__(parent)
        self.highlightingRules = []
        
        # headings
        Format = QTextCharFormat()
        Format.setForeground(QColor('#3536A9'))
        Format.setFontWeight(QFont.Bold)
        self.highlightingRules.append((QtCore.QRegExp("={2,}"), Format))     # minumum two '='
        self.highlightingRules.append((QtCore.QRegExp("[A-Z]+\s"), Format))  # word in upper letters with following whitespace
        self.highlightingRules.append((QtCore.QRegExp("([A-Z]+)$"), Format)) # last word in upper letters
        # Variables
        Format = QTextCharFormat()
        Format.setFontItalic(True)
        self.highlightingRules.append((QtCore.QRegExp("[A-Za-z0-9_-]+\:\s"), Format))
        # numbers
        Format = QTextCharFormat()
        Format.setForeground(QColor('#008000'))
        self.highlightingRules.append((QtCore.QRegExp("(^|\s|-|/)[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?"), Format))
        # comments in brackets
        Format = QTextCharFormat()
        Format.setForeground(QColor('#6C6C6C'))
        self.highlightingRules.append((QtCore.QRegExp("\(([^)]+)\)"), Format))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QtCore.QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)


class _report:
    def __init__(self, reportEdit):
        self.search = ''
        self.search_idx = -1
        self.reportEdit = reportEdit
        self.reportEdit.setCurrentFont(QFont(config['report_txt']['font'],
                                       config['report_txt']['fontsize']))
        
    def find(self, search):
        '''
        Finding and selection of strings in the report
        '''
        def reset_curser():
            c = self.reportEdit.textCursor()
            c.setPosition(0)
            self.reportEdit.setTextCursor(c) 
       
        def select(start, end):
            cursor = self.reportEdit.textCursor()
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.KeepAnchor)
            self.reportEdit.setTextCursor(cursor) 
        
        if not search:
            reset_curser()
            return 0
        
        if search != self.search:
            self.search = search
            text = self.reportEdit.toPlainText()
            self.found = []
            
            p = re.compile(search, flags=re.IGNORECASE)
            for p in p.finditer(text):
                self.found.append(p)
            if self.found:
                self.search_idx = -1
            else:
                self.search_idx = None
                reset_curser()
        
        if self.found:
            self.search_idx += 1
            if self.search_idx > len(self.found)-1:
                self.search_idx = 0
            select(self.found[self.search_idx].start(), self.found[self.search_idx].end())
            return len(self.found)
        else:
            return -1





