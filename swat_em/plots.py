# -*- coding: utf-8 -*-
'''
Provides functions for plotting
''' 
#  import time
#  import pdb

from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QFont
from swat_em.config import get_phase_color
import matplotlib as mpl
import matplotlib.pyplot as plt
#  from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
#  import matplotlib.patches as patches
import numpy as np

#  import time



class slot_plot:
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
        self.fig = plt.figure(1, dpi=self.data.config['plt']['DPI'])
        self.fig.clf()
        self.canvas1 = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas1)
        self.canvas1.draw()
        self.toolbar1 = NavigationToolbar(self.canvas1, 
                self.widget, coordinates=True)
        self.toolbar1.setFixedHeight(25)
        self.layout.addWidget(self.toolbar1)
        #  self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick_wdglayout)

       
    
    def plot_slots(self, Q):
        if Q <= 0:
            return False
        sh = self.sh  # slot height
        sw = self.sw  # slot width
        so = self.so  # slot opening


        
        plt.figure(1)
        #  self.fig1.clf()
        plt.clf()
        plt.axis('equal')
        self.ax = plt.gca()
        self.ax.axis('off')
        plt.subplots_adjust(left=0, bottom=0, right=1, top=1)
    
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
            plt.plot(xp[k], yp[k], 'k')
        
        i_slots = 0
        dy = 0
        dx = 0
        for k in range(Q):
            if i_slots >= 12:
                dx = 0
                dy += -1.5
                i_slots = 0
            plt.text(0.5+dx, -0.3+dy, str(k+1), horizontalalignment='center')
            dx += 1
            i_slots += 1
        
        self.canvas1.draw()
    

                        
    def plot_coilsides(self):
        S = self.data.machinedata['phases']
        Q = self.data.machinedata['Q']
        self.devide = 'v' if self.data.machinedata['wstep'] == 1 else 'h'
        
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
            
            t = plt.text(dx, 
                         dy, 
                         txt, horizontalalignment='center',
                         verticalalignment='center',
                         color = get_phase_color(self.data.config, phase-1),
                         rasterized=False,
                         weight = 'bold')
        
        #  t1 = time.time()
        for m, phase in enumerate(S):
            pos = 0
            for layer in phase:
                for cs in layer:
                    add_text(abs(cs), m+1, pos, cs)
                pos += 1
        self.canvas1.draw()
        #  print('duration for txt plot:', time.time()-t1)

   
    #  def onclick_wdglayout(self, event):
        #  Q = self.data.machinedata['Q']
        #  slot_select = int(event.xdata)+1
        #  slot_select = 1 if slot_select < 1 else slot_select
        #  slot_select = Q if slot_select > Q else slot_select
        #  print('selected slot: '+str(slot_select))
        #  print(event.xdata, event.ydata)
        



class slot_star:

    def __init__(self, layout, widget, data, table):
        self.layout = layout
        self.widget = widget
        self.data = data
        self.table = table

        self.fig = plt.figure(2, dpi=self.data.config['plt']['DPI'])
        self.fig.clf()
        plt.subplots_adjust(left=0, bottom=0, right=1, top=1)
        self.canvas1 = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas1)
        self.canvas1.draw()
        self.toolbar1 = NavigationToolbar(self.canvas1, 
                self.widget, coordinates=True)
        self.toolbar1.setFixedHeight(25)
        self.layout.addWidget(self.toolbar1)
        
    
    def plot_star(self, harmonic_idx = 0, ForceX = None):
        if harmonic_idx < 0:
            harmonic_idx = 0
        
        fig = plt.figure(2)
        plt.clf()
        
        xlim = [0, 0] # find limit manually, because autoscale doesn't work with plt.arrow()
        ylim = [0, 0]
        def plot_vek(vek, color='k', dangle = None):
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
                
                plt.arrow( old.real, old.imag, vek[k].real, vek[k].imag, head_width=0.08, fc=color, ec=color, linewidth=self.data.config['plt']['lw'])
                old = v[k]
            plt.plot( [0.0, v[-1].real], [0.0, v[-1].imag], '--', color = color, linewidth=self.data.config['plt']['lw'])
        
        if ForceX:
            angle_phase1 = np.angle(np.sum(self.data.results['Ei_el'][harmonic_idx][0]))
        else:
            angle_phase1 = None
        for k in range(len(self.data.results['Ei_el'][harmonic_idx])):
            plot_vek(self.data.results['Ei_el'][harmonic_idx][k], color = get_phase_color(self.data.config, k), dangle = angle_phase1)

        plt.axis('equal')
        ax = plt.gca()
        # ax.autoscale_view()
        ax.axis('off')
        
        # set limit manually, because autoscale doesn't work with plt.arrow()
        plt.xlim(xlim[0]*1.1, xlim[1]*1.1)
        plt.ylim(ylim[0]*1.1, ylim[1]*1.1)
        ax.set_adjustable("box")   # necessary for xlim/ylim with axis('equal')
        
          
        l = ['Phase '+str(k+1) for k in range(self.data.machinedata['m'])]
        leg = plt.legend(l,loc='upper right',labelspacing=0)    # labelspacing: Zeilenabstand
        leg.draw_frame(0)    # Rahmen nicht zeichnen
        self.canvas1.draw()
        
        
        # update table:        
        ei = self.data.results['Ei_el'][harmonic_idx]        
        
        self.table.setRowCount(len(ei))
        self.table.setColumnCount(3)
        
        for km in range(len(ei)):
            A = np.abs( np.sum(ei[km]) )
            ph = np.angle( np.sum(ei[km]) )/np.pi*180
            self.table.setItem(km, 0, QTableWidgetItem(str(km+1)))
            self.table.setItem(km, 1, QTableWidgetItem(str(round(A,1))))
            self.table.setItem(km, 2, QTableWidgetItem(str(round(ph,1))))

        for k1 in range(len(ei)):
            self.table.resizeColumnToContents(k1)


        self.table.setHorizontalHeaderLabels(['m', 'A', 'phase'])
        #  self.table.setVerticalHeaderLabels(['']*np.shape(kw)[0])
        afont = QFont()
        afont.setBold(True)
        
        for k in range(3):
            self.table.horizontalHeaderItem(k).setFont(afont)


class windingfactor:
    def __init__(self, layout, widget, data, table):
        self.layout = layout
        self.widget = widget
        self.data = data
        self.table = table

        self.fig = plt.figure(3, dpi=self.data.config['plt']['DPI'])
        self.fig.clf()
        self.canvas1 = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas1)
        self.canvas1.draw()
        self.toolbar1 = NavigationToolbar(self.canvas1, 
                self.widget, coordinates=True)
        self.toolbar1.setFixedHeight(25)
        self.layout.addWidget(self.toolbar1)
        
    
    def plot_windingfactor(self, mechanical = False):
        plt.figure(3)
        plt.clf()
        
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
            plt.bar( x, np.abs(kw[:,k]), (dx)/1.5/N, label = 'Phase '+str(k+1),
                color = get_phase_color(self.data.config, k))

        #  plt.title('Windingfactor')
        plt.xlabel('ordinal number $\\nu$')
        plt.ylabel('Windingfactor $|\\xi_w|$')
        plt.grid(True)
        ax = plt.gca()
        ax.set_axisbelow(True)  # grid in background        
        leg = plt.legend(loc='upper right',labelspacing=0)    # labelspacing: Zeilenabstand
        #  ltext = leg.get_texts() # all the text.Text instance in the legend
        #  plt.setp(ltext, fontsize='small') # the legend text fontsize
        #  plt.tight_layout()
        self.canvas1.draw()
        
        # update table:
        self.table.setRowCount(np.shape(kw)[0])
        self.table.setColumnCount(N+1)
        
        for k1 in range(np.shape(kw)[0]):
            self.table.setItem(k1, 0, QTableWidgetItem(str(nu[k1])))
            for k2 in range(np.shape(kw)[1]):
                self.table.setItem(k1, k2+1, QTableWidgetItem(str(round(kw[k1,k2],3))))
        for k1 in range(np.shape(kw)[0]):
            self.table.resizeColumnToContents(k1)


        self.table.setHorizontalHeaderLabels(['nu'] + self.data.machinedata['phasenames'])
        self.table.setVerticalHeaderLabels(['']*np.shape(kw)[0])
        afont = QFont()
        afont.setBold(True)
        
        for k in range(self.data.machinedata['m'] + 1):
            self.table.horizontalHeaderItem(k).setFont(afont)


class mmk:

    def __init__(self, layout, widget, data, table):
        self.layout = layout
        self.widget = widget
        self.data = data
        self.table = table

        self.fig = plt.figure(4, dpi=self.data.config['plt']['DPI'])
        self.fig.clf()
        plt.subplots_adjust(left=0, bottom=0, right=1, top=1)
        self.canvas1 = FigureCanvas(self.fig)
        self.layout.addWidget(self.canvas1)
        self.canvas1.draw()
        self.toolbar1 = NavigationToolbar(self.canvas1, 
                self.widget, coordinates=True)
        self.toolbar1.setFixedHeight(25)
        self.layout.addWidget(self.toolbar1)
        
    
    def plot_mmk(self):
        '''
        Plottet MMF-Kurve

        Parameters
        ----------
        plot_MMK_nu :           iterable - list/tuple
                                Liste/Tuple mit Ordnungszahlen, die geplottet werden sollen
        plot_MMK_greater_than : scalar, float
                                Plotte alle Oberschwingungen mit der Amplitude größer als
        '''
        
        plot_MMK_greater_than = 0.15

        plt.figure(4)
        plt.clf()
        
        MMK =  self.data.results['MMK']['MMK']
        phi = np.array(self.data.results['MMK']['phi'])
        theta = self.data.results['MMK']['theta']           

        plt.plot( phi, MMK, linewidth = self.data.config['plt']['lw'], label = 'MMF')
        
        
        #  plt.xlim(xmin=0, xmax=max(phi/np.pi*180))
        plt.grid(True)
        #  plt.title('Felderregerkurve')
        plt.ylabel('MMF in A')
        plt.xlabel('circumferential Stator in deg')

        # Plotte Oberschwingungen
        nu = np.array(self.data.results['MMK']['nu'])
        HA = self.data.results['MMK']['HA']

        A = np.abs(HA)
        phase = np.angle(HA)

        for n, a, p in zip(nu, A, phase):
            if 1/max(A)*a > plot_MMK_greater_than:
                plt.plot( phi, a*np.cos(n*phi/phi[-1]*2*np.pi + p), '--', label='$\\nu={}$'.format(n), linewidth=self.data.config['plt']['lw_thin'])

        leg = plt.legend(loc='upper right',labelspacing=0)
        plt.xlim(min(phi), max(phi))
        
        #  ax = plt.gca()
        #  ax2 = ax.twinx()
        #  ax2.stem(range(len(theta)), theta, 'r', markerfmt=' ')            

        plt.tight_layout()
        self.canvas1.draw()
        
        
        # update table:
        self.table.setRowCount(len(A)-1)
        self.table.setColumnCount(3)
        
        self.table.setHorizontalHeaderLabels(['nu', 'Amp', '[%]'])
        #  self.table.setVerticalHeaderLabels(['']*np.shape(kw)[0])
        
        
        for k1 in range(1, len(A)):
            self.table.setItem(k1-1, 0, QTableWidgetItem(str(nu[k1])))
            a = A[k1]
            a_rel = 100.0/max(A)*a
            self.table.setItem(k1-1, 1, QTableWidgetItem(str(round(a, 3))))
            self.table.setItem(k1-1, 2, QTableWidgetItem(str(round(a_rel, 1))))
            #  for k2 in range(np.shape(kw)[1]):
                #  self.table.setItem(k1, k2+1, QTableWidgetItem(str(round(kw[k1,k2],3))))
        for k1 in range(3):
            self.table.resizeColumnToContents(k1)


        
        #  afont = QFont()
        #  afont.setBold(True)
        
        #  for k in range(self.data.machinedata['m'] + 1):
            #  self.table.horizontalHeaderItem(k).setFont(afont)
