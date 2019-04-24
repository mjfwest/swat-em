# -*- coding: utf-8 -*-

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMessageBox
import sys
import os
from swat_em import config

__dir__ = os.path.dirname(os.path.abspath(__file__))

class Settings(QDialog):
    def __init__(self, config):
        self.config = config
        super().__init__()
        #  self.resetted = False # flag is set, if user reset the config
       
        # Set up the user interface from Designer.
        uic.loadUi(os.path.join(__dir__, 'ui/Settings.ui'), self)
        self.setWindowTitle('Settings')
        
        #  self.Button_CANCEL.clicked.connect(self.reject)
        #  self.Button_OK.clicked.connect(self.accept)
        self.Button_RESET.clicked.connect(self.reset)

        # Nothing is done, when a value is changed, yet
        # later here can be checked for plausibility
        
        #  self.spinBox_nu_el.valueChanged.connect(self.update)
        #  self.spinBox_nu_mech.valueChanged.connect(self.update)
        #  self.spinBox_nu_MMK.valueChanged.connect(self.update)
        #  self.doubleSpinBox_threshold_wf.valueChanged.connect(self.update)
        
    def reset(self):
        ok = QMessageBox.question(self, 'Reset settings', "Do you want to reset the settings to default values?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ok == QMessageBox.Yes:
            #  self.resetted = True
            self.config = config.get_init_config()
            self.write_to_gui()

    # Nothing is done, when a value is changed, yet
    # later here can be checked for plausibility
    #  def update(self):
        #  print('update')


    def write_to_gui(self):
        '''
        Write the config values to the cui
        '''
        self.spinBox_nu_el.setValue(self.config['N_nu_el'])
        self.spinBox_nu_mech.setValue(self.config['N_nu_mech'])
        self.spinBox_nu_MMK.setValue(self.config['max_nu_MMK'])
        self.doubleSpinBox_threshold_wf.setValue(self.config['kw_min'])
        
        self.spinBox_DPI.setValue(self.config['plt']['DPI'])
        self.doubleSpinBox_lw.setValue(self.config['plt']['lw'])
        self.doubleSpinBox_lw_thin.setValue(self.config['plt']['lw_thin'])

    def read_from_gui(self):
        '''
        Read the config values from the cui
        '''
        self.config['N_nu_el'] = self.spinBox_nu_el.value()
        self.config['N_nu_mech'] = self.spinBox_nu_mech.value()
        self.config['max_nu_MMK'] = self.spinBox_nu_MMK.value()
        self.config['kw_min'] = self.doubleSpinBox_threshold_wf.value() 
        
        self.config['plt']['DPI'] = self.spinBox_DPI.value()
        self.config['plt']['lw'] = self.doubleSpinBox_lw.value()
        self.config['plt']['lw_thin'] = self.doubleSpinBox_lw_thin.value()
        
        


    def run(self):        
        self.write_to_gui()
        
        ok = self.exec_()
        if ok:
            self.read_from_gui()
            return self.config
















