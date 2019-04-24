# -*- coding: utf-8 -*-

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QTableWidgetItem
import sys
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)

#  sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
__dir__ = os.path.dirname(os.path.abspath(__file__))



class Factors(QDialog):
    def __init__(self, data, config):
        self.config = config
        self.data = data
        super().__init__()
       
        # Set up the user interface from Designer.
        uic.loadUi(os.path.join(__dir__, 'ui/Factors.ui'), self)
        self.setWindowTitle('Additional factors')
        
        self.groupBox_1.toggled.connect(self.update)
        self.groupBox_2.toggled.connect(self.update)
        self.groupBox_3.toggled.connect(self.update)
        
        self.doubleSpinBox_Ds.valueChanged.connect(self.update)
        self.doubleSpinBox_s.valueChanged.connect(self.update)
        self.doubleSpinBox_skew.valueChanged.connect(self.update)
        self.doubleSpinBox_alpha.valueChanged.connect(self.update)
        

        #  self.radioButton_slayer.toggled.connect(self.change_layers) # disable lineEdit for single phase windings
        
        self.fig = plt.figure(5, dpi=90)
        self.fig.clf()
        self.canvas1 = FigureCanvas(self.fig)
        self.mplvl_factors.addWidget(self.canvas1)
        self.canvas1.draw()
        self.toolbar1 = NavigationToolbar(self.canvas1, 
                self.mplwidget_factors, coordinates=True)
        self.toolbar1.setFixedHeight(25)
        self.mplvl_factors.addWidget(self.toolbar1)
        

    def update(self):
        print('update')


    def run(self):
        self.update()  # calc initial
        ok = self.exec_()
        if ok:
            print('return something')
















