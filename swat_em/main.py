# -*- coding: utf-8 -*-

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt5.QtGui import QIntValidator
import sys
import os
import time
import argparse


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from swat_em import dialog_genwdg
from swat_em import dialog_about
from swat_em import dialog_winding_layout
from swat_em import dialog_factors
from swat_em import dialog_settings
from swat_em.config import get_config, save_config
from swat_em import datamodel
from swat_em import wdggenerator
from swat_em import plots

__dir__ = os.path.dirname(os.path.abspath(__file__))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.data = datamodel.datamodel()
        self.config = get_config(default = False)
        self.data.set_config(self.config)

        # Set up the user interface from Designer.
        uic.loadUi(os.path.join(__dir__, 'ui/MainWindow.ui'), self)
        self.setWindowTitle('SWAT')

        self.DIALOG_GenWinding = dialog_genwdg.GenWinding2(self.config)
        self.DIALOG_GenWindingCombinations = dialog_genwdg.GenWindingCombinations(self.config)
        self.DIALOG_AdditionalFactors = dialog_factors.Factors(self.config, self.data)

        # Connect up the buttons.
        self.Button_exit.clicked.connect(self.close)
        self.Button_EditWindingLayout.clicked.connect(self.dialog_EditWindingLayout)
        self.Button_GenerateAutomatically.clicked.connect(self.dialog_GenWinding)
        self.Button_FindByTable.clicked.connect(self.dialog_GenWindingCombinations)
        
        # Connect menu
        self.actionExit.triggered.connect(self.close)
        self.actionGenerate_winding.triggered.connect(self.dialog_GenWinding)
        self.actionGenerate_winding_combinations.triggered.connect(self.dialog_GenWindingCombinations)
        
        self.actionsave.triggered.connect(self.save_to_file)
        self.actionsave_as.triggered.connect(self.save_as_to_file)
        self.actionload.triggered.connect(self.load_from_file)
        self.actionProgram_Info.triggered.connect(dialog_about.about)
        self.actionShow_winding_layout.triggered.connect(self.dialog_EditWindingLayout)
        self.actionAdditional_factors.triggered.connect(self.dialog_AdditionalFactors)
        self.actionSettings.triggered.connect(self.dialog_settings)
        
        # TODO
        self.actionprint_report.triggered.connect(lambda: QMessageBox.information(self, 'Information', 'Not implemented yet'))
        self.actionHelp.triggered.connect(lambda: QMessageBox.information(self, 'Information', 'Not implemented yet'))
        
        self.plot_tabs.currentChanged.connect(self.update_plot_in_GUI)
        self.radioButton_electrical.toggled.connect(self.update_plot_in_GUI)
        self.comboBox_star_harmonics.currentIndexChanged.connect(self.update_plot_in_GUI)
        self.checkBoxForceX.toggled.connect(self.update_plot_in_GUI)
        

        #  initial winding  -----------------------------------
        self.data.set_machinedata(Q = 12, p = 10/2, m = 3)
        wdglayout = wdggenerator.genwdg(
                            self.data.machinedata['Q'], 
                            2*self.data.machinedata['p'], 
                            self.data.machinedata['m'], 
                            w = 1, 
                            layers = 2)
        #  ----------------------------------------------------
        
        self.data.set_phases(S = wdglayout['phases'], wstep = wdglayout['wstep'])
        self.data.set_valid(valid = wdglayout['valid'], error = wdglayout['error'])
        self.data.analyse_wdg()
        self.data.actual_state_saved = True # Simulate save state
        
        # output table
        #  self.tableView_wdginfo.setAlternatingRowColors(True)
        #  self.tableView_wdginfo.setStyleSheet("alternate-background-color: #DCDCDC;")
        
        
        # Plots
        self.fig1 = plots.slot_plot(self.mplvl_slot, self.mplwidget_slot, self.data)
        self.fig2 = plots.slot_star(self.mplvl_star, self.mplwidget_star, self.data, self.tableWidget_star)
        self.fig3 = plots.windingfactor(self.mplvl_wf, self.mplwidget_wf, self.data, self.tableWidget_wf)
        self.fig4 = plots.mmk(self.mplvl_mmk, self.mplwidget_mmk, self.data, self.tableWidget_mmk)
        
        self.update_data_in_GUI()        
        self.show()


    def dialog_GenWinding(self):
        '''
        calls the dialog to generate a single winding
        '''
        ret = self.DIALOG_GenWinding.run()
        if ret:
            wdglayout = wdggenerator.genwdg(ret['Q'], ret['P'], ret['m'], ret['w'], ret['layers'])
            self.data.set_machinedata(Q = ret['Q'], p = ret['P']//2, m = ret['m'])
            self.data.set_phases(wdglayout['phases'], wstep = wdglayout['wstep'])            
            self.data.analyse_wdg()
            self.data.set_valid(valid = wdglayout['valid'], error = wdglayout['error'])            
            self.update_data_in_GUI()


    def dialog_GenWindingCombinations(self):
        '''
        calls the dialog to generate a winding based on a big table of available windings
        '''
        ret = self.DIALOG_GenWindingCombinations.run()
        if ret:
            wdglayout = wdggenerator.genwdg(ret['Q'], ret['P'], ret['m'], ret['w'], ret['layers'])
            self.data.set_machinedata(Q = ret['Q'], p = ret['P']//2, m = ret['m'])
            self.data.set_phases(wdglayout['phases'], wstep = wdglayout['wstep'])            
            self.data.analyse_wdg()
            self.data.set_valid(valid = wdglayout['valid'], error = wdglayout['error'])            
            self.update_data_in_GUI()


    def dialog_EditWindingLayout(self):
        '''
        calls the dialog to generate a winding based on a big table of available windings
        '''
        DIALOG_EditWindingLayout = dialog_winding_layout.layout(self.data)
        ret = DIALOG_EditWindingLayout.run()

        if ret:
            self.data.set_machinedata(Q = ret['Q'], p = ret['P']//2, m = ret['m'])
            self.data.set_phases(ret['phases'], wstep = ret['w'])            
            self.data.analyse_wdg()
            #  self.data.set_valid(valid = wdglayout['valid'], error = wdglayout['error'])            
            self.update_data_in_GUI()


    def dialog_AdditionalFactors(self):
        ret = self.DIALOG_AdditionalFactors.run()


    def dialog_settings(self):
        DIALOG_Settings = dialog_settings.Settings(self.config)
        ret = DIALOG_Settings.run()
        if ret:
            self.config = ret
            save_config(self.config)
            self.data.analyse_wdg()   # recalc the winding model
            self.update_data_in_GUI()


    def update_data_in_GUI(self):
        '''
        plots all winding data in gui
        '''
        t1 = time.time()
        # Update line edits
        #  self.lineEdit_P.blockSignals(True)  # turn off signals to prevent trigger during update
        #  self.lineEdit_P.setText(str(int(self.data.machinedata['p']*2)))
        #  self.lineEdit_P.blockSignals(False)
        
        #  self.lineEdit_m.blockSignals(True)
        #  self.lineEdit_m.setText(str(self.data.machinedata['m']))
        #  self.lineEdit_m.blockSignals(False)
        
        #  self.lineEdit_Q.blockSignals(True)
        #  self.lineEdit_Q.setText(str(self.data.machinedata['Q']))
        #  self.lineEdit_Q.blockSignals(False)
        
        
        # Update machine infos
        # TODO: fundamental windingfactor        
        bc, bc_str = self.data.get_basic_characteristics()
        #  self.textBrowser_wdginfo.setPlainText(bc_str)
        
        # New info in tableView
        #  self.tableView_wdginfo.setColumnCount(3) 
        #  self.tableView_wdginfo.setRowCount(3)
        
        #  descr = ['Number of slots', 'Number of phases', 'Number of Poles']
        #  symb  = ['Q', 'm', '2p']
        #  for k in range(len(descr)):
            #  self.tableView_wdginfo.setItem(k, 0, QTableWidgetItem(descr[k]))
            #  self.tableView_wdginfo.setItem(k, 1, QTableWidgetItem(symb[k]))

        #  self.tableView_wdginfo.setItem(0, 2, QTableWidgetItem(str(self.data.machinedata['Q'])))
        #  self.tableView_wdginfo.setItem(1, 2, QTableWidgetItem(str(self.data.machinedata['m'])))
        #  self.tableView_wdginfo.setItem(2, 2, QTableWidgetItem(str(self.data.machinedata['p']*2)))
        
        #  for k in range(3):
            #  self.tableView_wdginfo.resizeColumnToContents(k)
        

        
        self.textBrowser_wdginfo.setHtml(bc_str)
        self.update_plot_in_GUI()
        
        self.comboBox_star_harmonics.blockSignals(True)   # prevent double plotting on startup
        self.comboBox_star_harmonics.clear()
        self.comboBox_star_harmonics.addItems([str(k) for k in self.data.results['nu_el']])
        self.comboBox_star_harmonics.blockSignals(False)
        
        
    def update_plot_in_GUI(self):
        # Update Figures
        idx = self.plot_tabs.currentIndex()
        # update only the current tab
        if idx == 0:
            self.fig1.plot_slots(self.data.machinedata['Q'])
            #  print('time for plotting:', time.time()-t1); t1 = time.time()
            self.fig1.plot_coilsides()
            #  print('time for plotting:', time.time()-t1); t1 = time.time()
        if idx == 1: 
            
            self.fig2.plot_star(harmonic_idx = self.comboBox_star_harmonics.currentIndex(), ForceX = self.checkBoxForceX.isChecked())
            #  print('time for plotting:', time.time()-t1); t1 = time.time()
        if idx == 2:
            if self.radioButton_electrical.isChecked():
                self.fig3.plot_windingfactor(mechanical=False)
            elif self.radioButton_mechanical.isChecked():
                self.fig3.plot_windingfactor(mechanical=True)
            #  print('time for plotting:', time.time()-t1); t1 = time.time()
        if idx == 3:  
            self.fig4.plot_mmk()
            #  print('time for plotting:', time.time()-t1); t1 = time.time()

        
    def save_to_file(self):
        '''
        returns True if file is saved
        '''
        if not self.data.filename:
            ret = self.save_as_to_file()
            return ret
        else:
            self.data.save_to_file(self.data.filename)
            return True


    def save_as_to_file(self):
        '''
        returns True if file is saved
        '''
        options = QFileDialog.Options()
        #  options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self,"Save winding file", "","Winding Files (*.wdg)", options=options)
        if filename:
            if not filename.endswith('.wdg'):
                filename += '.wdg'
            self.data.set_filename(filename) 
            self.data.save_to_file(self.data.filename)
            return True
        else:
            return False


    def load_from_file(self):
        if not self.data.actual_state_saved:
            ok = QMessageBox.question(self, 'Exit program', "Do you want to save?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
            if ok == QMessageBox.Yes:
                ret = self.save_to_file()
                if not ret: # user has not saved
                    return
            if ok == QMessageBox.Cancel: # cancel
                return

        
        options = QFileDialog.Options()
        #  options |= QFileDialog.DontUseNativeDialog  # use qt5 dialog instead of os default
        filename, _ = QFileDialog.getOpenFileName(self,"Open winding file", "","Winding Files (*.wdg)", options=options)
        if filename:
            self.data.load_from_file(filename)
            self.data.set_filename(filename)
            self.update_data_in_GUI()
        
    
    def closeEvent(self, event):
        # Exit programm
        
        # Ask for saving
        if self.data.actual_state_saved:
            event.accept() # let the window close
        else:
            #  print('ask for saving')
            ok = QMessageBox.question(self, 'Exit program', "Do you want to save?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
            if ok == QMessageBox.Yes:
                ret = self.save_to_file()
                if ret:  # user has saved
                    event.accept() # let the window close
                else:    # user has not saved
                    event.ignore()
            elif ok == QMessageBox.No:
                event.accept() # close the window
            else:
                event.ignore() # let the window open
                


def main():
    # command line options
    parser = argparse.ArgumentParser(
        prog = 'SWAT-EM',
        description='Generating and evaluating of windings for electrial machines', 
        formatter_class=argparse.RawTextHelpFormatter)
    
    parser.add_argument(action='store', nargs='?', default='', dest='arg_1', help='*.py scriptfile or *.wdg file')
    parser.add_argument('--load', action='store', default='', dest='loadfile', help='Open an existing *.wdg file')
    parser.add_argument('--script', action='store', default='', dest='scriptfile', help='Open an existing *.py script file')
    args = parser.parse_args()
    
    if len(args.arg_1) > 0:
        #  print('my arg: ', args.arg_1)
        ext = os.path.splitext(args.arg_1)[-1]
        if ext.upper() == '.PY':
            args.scriptfile = args.arg_1
        elif ext.upper() == '.WDG':
            args.loadfile = args.arg_1
    
    if args.scriptfile:
        print('eval script file:', args.scriptfile)
    else:
        print('running GUI')
        app = QApplication(sys.argv)
        ex = MainWindow()
        
        if args.loadfile:
            if os.path.isfile(args.loadfile):
                ex.data.load_from_file(args.loadfile)
                ex.data.set_filename(args.loadfile)
                ex.update_data_in_GUI()
            else:
                raise(Exception, 'file not found:'.format(args.loadfile))
        
        sys.exit(app.exec_())


if __name__ == '__main__':
    main()
    
    
    
