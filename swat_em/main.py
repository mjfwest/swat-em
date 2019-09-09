# -*- coding: utf-8 -*-
import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog,\
                            QInputDialog, QMessageBox, QListWidgetItem,\
                            QMenu, QAction, QSplashScreen
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QIcon,QPixmap
from PyQt5 import QtCore

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
__dir__ = os.path.dirname(os.path.abspath(__file__))

# Create a splash screen while loading the librarys because this
# takes some time
app = QApplication([])  # temp. app needed for splash
splash_pix = QPixmap(os.path.join(__dir__, 'ui', 'bitmaps', 'splash.png'))
splash = QSplashScreen(splash_pix, QtCore.Qt.WindowStaysOnTopHint)
splash.show()

import time
import argparse
import subprocess
import platform
from swat_em import dialog_genwdg
from swat_em import dialog_about
from swat_em import dialog_notes
from swat_em import dialog_winding_layout
from swat_em import dialog_import_winding
from swat_em import dialog_factors
from swat_em import dialog_settings
from swat_em.config import config, save_config
from swat_em import datamodel
from swat_em import wdggenerator
from swat_em import plots
from swat_em.analyse import get_float

MSG_TIME = 3000   # time in which the message is displayed in the statusbar



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.data = datamodel.datamodel()
        self.project = datamodel.project()

        # Set up the user interface from Designer.
        uic.loadUi(os.path.join(__dir__, 'ui', 'MainWindow.ui'), self)
        self.setWindowTitle('SWAT-EM')

        self.DIALOG_GenWinding = dialog_genwdg.GenWinding2()
        self.DIALOG_GenWindingCombinations = dialog_genwdg.GenWindingCombinations()
        self.DIALOG_AdditionalFactors = dialog_factors.Factors(self.data)

        # Connect the buttons
        self.Button_exit.clicked.connect(self.close)
        
        self.projectlist_Button_new.clicked.connect(self.dialog_new_winding)
        self.projectlist_Button_delete.clicked.connect(self.projectlist_delete)
        self.projectlist_Button_clone.clicked.connect(self.projectlist_clone)
        self.projectlist_Button_notes.clicked.connect(self.dialog_get_notes)
        self.projectlist_Button_manual.clicked.connect(self.dialog_EditWindingLayout)
        self.projectlist_Button_auto.clicked.connect(self.dialog_GenWinding)
        self.projectlist_Button_table.clicked.connect(self.dialog_GenWindingCombinations)
        
        # Connect menu
        self.actionExit.triggered.connect(self.close)
        self.actionNew_winding.triggered.connect(self.dialog_new_winding)
        self.actionGenerate_winding.triggered.connect(self.dialog_GenWinding)
        self.actionGenerate_winding_combinations.triggered.connect(self.dialog_GenWindingCombinations)
        self.actionImport_from_file.triggered.connect(self.dialog_ImportWinding)
        self.actionAdd_Notes.triggered.connect(self.dialog_get_notes)
        
        self.actionsave.triggered.connect(self.save_to_file)
        self.actionsave_as.triggered.connect(self.save_as_to_file)
        self.actionload.triggered.connect(self.load_from_file)
        self.actionProgram_Info.triggered.connect(dialog_about.about)
        self.actionShow_winding_layout.triggered.connect(self.dialog_EditWindingLayout)
        self.actionAdditional_factors.triggered.connect(self.dialog_AdditionalFactors)
        self.actionSettings.triggered.connect(self.dialog_settings)
        self.actionundo.triggered.connect(self.undo)
        self.actionredo.triggered.connect(self.redo)
        
        # Connect project models
        self.project_listWidget.currentRowChanged.connect(self.update_project) 
        self.project_listWidget.itemChanged.connect(self.projectlist_rename)    # item renamed


                        
        # context-menu on project models
        self.project_listWidget.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)

        self.actionClone = QAction("clone", self.project_listWidget, 
                   icon=QIcon(os.path.join(__dir__, 'ui', 'icons', 'clone.png')))
        self.project_listWidget.addAction(self.actionClone)
        self.actionClone.triggered.connect(self.projectlist_clone)
        
        self.actionNotes = QAction("add notes", self.project_listWidget, 
                   icon=QIcon(os.path.join(__dir__, 'ui', 'icons', 'notes.png')))
        self.project_listWidget.addAction(self.actionAdd_Notes)
        self.actionNotes.triggered.connect(self.projectlist_clone)
        
        self.actionDelete = QAction("delete", self.project_listWidget, 
                   icon=QIcon(os.path.join(__dir__, 'ui', 'icons', 'delete.png')))        
        self.project_listWidget.addAction(self.actionDelete)
        self.actionDelete.triggered.connect(self.projectlist_delete)



        # TODO
        self.actionprint_report.triggered.connect(lambda: QMessageBox.information(self, 'Information', 'Not implemented yet'))
        self.actionHelp.triggered.connect(self.open_manual)
        
        self.plot_tabs.currentChanged.connect(lambda: self.update_plot_in_GUI(small_update = False))
        self.radioButton_electrical.toggled.connect(self.update_plot_in_GUI)
        self.comboBox_star_harmonics.currentIndexChanged.connect(self.update_plot_in_GUI)
        self.checkBoxForceX.toggled.connect(self.update_plot_in_GUI)
        

        #  initial windings  -----------------------------------
        self.data = datamodel.datamodel()
        self.data.genwdg(Q = 12, P = 2, m = 3, w = -1, layers = 1)
        self.data.set_notes('Winding example for a overlapping single layer winding for a 12 slots, 10 poles machine')
        self.data.set_title('12-2 overlapping winding')
        self.project.add_model(self.data)

        self.data = datamodel.datamodel()
        self.data.genwdg(Q = 9, P = 8, m = 3, w = 1, layers = 2, turns = 10)
        self.data.set_notes('Winding example for a tooth-coil-winding for 9 slots, 8 poles machine')
        self.data.set_title('9-8 tooth-coil winding')
        self.project.add_model(self.data)
        
        self.project.set_actual_state_saved()  # only for the initial winding
        
        
        # Plots
        self.MMK_phase_edit.setValidator(QDoubleValidator(0, 360, 1))
        self.MMK_phase_edit.setText(str(0.000))
        
        #  self.MMK_phase_slider.valueChanged.connect(self.update_plot_in_GUI)
        self.MMK_phase_slider.valueChanged.connect(self.update_MMK_phase_edit)
        self.MMK_phase_edit.textEdited.connect(self.update_MMK_phase_slider)
        self.MMK_phase_edit.textChanged.connect(lambda: self.update_plot_in_GUI(small_update = True))
        
        self.fig1 = plots.slot_plot(self.mplvl_slot, self.mplwidget_slot, self.data)
        self.fig2 = plots.slot_star(self.mplvl_star, self.mplwidget_star, self.data, self.tableWidget_star)
        self.fig3 = plots.windingfactor(self.mplvl_wf, self.mplwidget_wf, self.data, self.tableWidget_wf)
        self.fig4 = plots.mmk(self.mplvl_mmk, self.mplwidget_mmk, self.data, self.tableWidget_mmk)
        
        self.update_project_list()
        #  self.update_data_in_GUI()     # not neccessary because of 'update_project_list()
        self.project.reset_undo_state()  # init-winding shouldn't undoable
        self.actionundo.setDisabled(True)
        self.actionredo.setDisabled(True)
        self.show()
    
    
    def save_undo_state(self):
        '''save the actual state of the project models for undo operation'''
        self.project.save_undo_state()
        self.actionundo.setDisabled(False)
        self.project.reset_redo_state() # redo states aren't valid any more
        self.actionredo.setDisabled(True)
        
    
    def undo(self):
        '''undo the last operation (restore state)'''
        self.project.save_redo_state()
        self.actionredo.setDisabled(False)
        self.project.undo()
        self.update_project_list()
        #  self.update_project()
        if self.project.get_num_undo_state() < 1:
            self.actionundo.setDisabled(True) # no more states to restore
        
    def redo(self):
        self.project.save_undo_state()
        self.actionundo.setDisabled(False)
        self.project.redo()
        self.update_project_list()
        #  self.update_project()
        if self.project.get_num_redo_state() < 1:
            self.actionredo.setDisabled(True) # no more states to restore
    
    
    def update_project_list(self, switch_to_new = False):
        '''fill the list of all data objects
        if 'switch_to_new = True: mark the last (new) object in project list 
        and show the content of it. If False: The last idx is marked again'''
        self.project_listWidget.blockSignals(True)
        idx = self.project_listWidget.currentRow() # save current idx
        self.project_listWidget.clear()            # clear existing data
        for i, item in enumerate(self.project.get_titles()):
            widgetitem = QListWidgetItem(item)
            widgetitem.setFlags(widgetitem.flags() | QtCore.Qt.ItemIsEditable)
            self.project_listWidget.addItem(widgetitem)
        self.project_listWidget.blockSignals(False)
        if switch_to_new:
            idx = i
        else:
            idx = i if i < idx else idx
            idx = 0 if idx < 0 else idx
        self.project_listWidget.setCurrentRow(idx)   # last item is current model
    
    def update_project(self, idx = None):
        '''update the clicked data object form the project'''
        if not idx:
            idx = self.project_listWidget.currentRow()
        self.data = self.project.get_model_by_index(idx)
        self.update_data_in_GUI()  # update all data output and figures
    
    def projectlist_delete(self):
        if self.project_listWidget.count() > 1:
            self.save_undo_state()  # for undo
            idx = self.project_listWidget.currentRow()
            self.project.delete_model_by_index(idx)
            self.statusbar.showMessage('winding deleted', MSG_TIME)
            self.update_project_list()
            self.statusbar.showMessage('winding cloned', MSG_TIME)
    
    def projectlist_clone(self):
        self.save_undo_state()  # for undo
        idx = self.project_listWidget.currentRow()
        self.project.clone_by_index(idx)
        self.statusbar.showMessage('winding cloned', MSG_TIME)
        self.update_project_list(switch_to_new = True)

    def projectlist_rename(self):
        self.save_undo_state()  # for undo
        idx = self.project_listWidget.currentRow()
        newname = self.project_listWidget.item(idx).text()
        self.project.rename_by_index(idx, newname)
    
    
    def update_MMK_phase_edit(self):
        '''slider for MMK phase moved'''
        self.MMK_phase_edit.setText(str(self.MMK_phase_slider.value()))


    def update_MMK_phase_slider(self):
        '''lineedit for MMK phase changed'''
        f = get_float(self.MMK_phase_edit.text())
        if f is not None:
            self.MMK_phase_slider.setValue(f)


    def dialog_GenWinding(self):
        '''
        calls the dialog to generate a single winding
        '''
        ret = self.DIALOG_GenWinding.run()
        if ret:
            self.save_undo_state()
            wdglayout = wdggenerator.genwdg(ret['Q'], ret['P'], ret['m'], ret['w'], ret['layers'])
            
            data = datamodel.datamodel()
            data.set_machinedata(Q = ret['Q'], p = ret['P']//2, m = ret['m'])
            data.set_phases(wdglayout['phases'], wstep = wdglayout['wstep'])            
            data.analyse_wdg()
            data.set_valid(valid = wdglayout['valid'], error = wdglayout['error'])            
            if ret['overwrite']:
                self.data = data
                self.project.replace_model_by_index(data, self.project_listWidget.currentRow())
            else:
                self.project.add_model(data)
                self.update_project_list(switch_to_new = True)
            self.update_data_in_GUI()


    def dialog_GenWindingCombinations(self):
        '''
        calls the dialog to generate a winding based on a big table of available windings
        '''
        ret = self.DIALOG_GenWindingCombinations.run()
        if ret:
            self.save_undo_state()
            wdglayout = wdggenerator.genwdg(ret['Q'], ret['P'], ret['m'], ret['w'], ret['layers'])
            
            data = datamodel.datamodel()
            data.set_machinedata(Q = ret['Q'], p = ret['P']//2, m = ret['m'])
            data.set_phases(wdglayout['phases'], wstep = wdglayout['wstep'])            
            data.analyse_wdg()
            data.set_valid(valid = wdglayout['valid'], error = wdglayout['error'])            
            if ret['overwrite']:
                self.data = data
                self.project.replace_model_by_index(data, self.project_listWidget.currentRow())
            else:
                self.project.add_model(data)
                self.update_project_list(switch_to_new = True)
            self.update_data_in_GUI()

    def dialog_ImportWinding(self):

        DIALOG_ImportWinding = dialog_import_winding.import_winding()
        ret = DIALOG_ImportWinding.run()
        if ret is not None:
            self.save_undo_state()  # for undo
            for data in ret:
                self.project.add_model(data)
            self.update_project_list(switch_to_new = True)
            self.statusbar.showMessage('{} winding(s) imported'.format(len(ret)), MSG_TIME)
        
        
    def dialog_EditWindingLayout(self):
        '''
        calls the dialog to generate a winding based on a big table of available windings
        '''
        DIALOG_EditWindingLayout = dialog_winding_layout.layout(self.data)
        ret = DIALOG_EditWindingLayout.run()

        if ret:
            self.save_undo_state()
            
            data = datamodel.datamodel()
            data.set_machinedata(Q = ret['Q'], p = ret['P']//2, m = ret['m'])
            data.set_phases(ret['phases'], wstep = ret['w'], turns = ret['turns'])
            data.analyse_wdg()
            #  data.set_valid(valid = wdglayout['valid'], error = wdglayout['error'])
            if ret['overwrite']:
                self.data = data 
                self.project.replace_model_by_index(data, self.project_listWidget.currentRow())
            else:
                self.project.add_model(data)
                self.update_project_list(switch_to_new = True)
            self.update_data_in_GUI()


    def dialog_AdditionalFactors(self):
        ret = self.DIALOG_AdditionalFactors.run()


    def dialog_get_notes(self):
        '''dialog asks user to type notes and stores it to datamodel'''
        dialog = dialog_notes.get_notes(self.data.notes)
        text = dialog.run()
        if text is not None:
            self.save_undo_state()
            self.data.set_notes(text)
            self.update_data_in_GUI()
        
    def dialog_new_winding(self):
        '''
        dialog to generate a new winding
        wraps the user input to the existing generators
        '''
        dialog = dialog_genwdg.NewWinding()
        ret = dialog.run()
        if ret is not None:
            if ret == 0:   # trigger the different generators
                self.dialog_EditWindingLayout()
            elif ret == 1:
                self.dialog_GenWinding()
            elif ret == 2:
                self.dialog_GenWindingCombinations()
            else:
                raise(Exception, 'winding generator {} not implemented'.format(ret))


    def dialog_settings(self):
        global config
        config
        DIALOG_Settings = dialog_settings.Settings(config)
        ret = DIALOG_Settings.run()
        if ret:
            config = ret
            save_config(config)
            self.data.analyse_wdg()   # recalc the winding model
            self.update_data_in_GUI()


    def update_data_in_GUI(self):
        '''
        plots all winding data in gui
        '''
        bc, bc_str = self.data.get_basic_characteristics()
        
        self.textBrowser_wdginfo.setHtml(bc_str)
        self.update_plot_in_GUI()
        
        self.comboBox_star_harmonics.blockSignals(True)   # prevent double plotting on startup
        self.comboBox_star_harmonics.clear()
        self.comboBox_star_harmonics.addItems([str(k) for k in self.data.results['nu_el']])
        self.comboBox_star_harmonics.blockSignals(False)
        
        
    def update_plot_in_GUI(self, small_update = False):
        '''
        update the current figure
        if 'small_update' is True, only new lines/bars are plottet and not the 
        all axes etc. --> speed up, for MMK-phase slider for example
        '''
        # Update Figures
        idx = self.plot_tabs.currentIndex()
        #  t1 = time.time()
        # update only the current tab
        if idx == 0:
            self.fig1.plot_slots(self.data.machinedata['Q'])
            self.fig1.plot_coilsides(self.data)
        if idx == 1: 
            self.fig2.plot_star(self.data, harmonic_idx = self.comboBox_star_harmonics.currentIndex(),
            ForceX = self.checkBoxForceX.isChecked())
        if idx == 2:
            if self.radioButton_electrical.isChecked():
                self.fig3.plot_windingfactor(self.data, mechanical=False)
            elif self.radioButton_mechanical.isChecked():
                self.fig3.plot_windingfactor(self.data, mechanical=True)
        if idx == 3:
            f = get_float(self.MMK_phase_edit.text())
            f = 0.0 if f is None else f
            self.fig4.plot_mmk(self.data, f, small_update = small_update)
        #  print('duration for plot:', time.time()-t1)

        
    def save_to_file(self):
        '''
        returns True if file is saved
        '''
        if not self.project.filename:
            ret = self.save_as_to_file()
            return ret
        else:
            self.project.save_to_file(self.project.filename)
            self.statusbar.showMessage('Project saved as ' + self.project.filename, MSG_TIME)
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
            self.project.set_filename(filename) 
            self.project.save_to_file(self.project.filename)
            self.statusbar.showMessage('Project saved as ' + self.project.filename, MSG_TIME)
            return True
        else:
            return False


    def load_from_file(self):
        if not self.project.get_actual_state_saved():
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
            self.project.load_from_file(filename)
            self.statusbar.showMessage('Project loaded: ' + filename, MSG_TIME)
            self.project.set_filename(filename)
            self.update_project_list()
            self.update_data_in_GUI()
        
    
    def closeEvent(self, event):
        # Exit programm
        
        # Ask for saving
        if self.project.get_actual_state_saved():
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
                
    def open_manual(self):
        doc = os.path.join(__dir__, 'doc', 'manual', 'manual.pdf')
        #  subprocess.Popen(['open', doc], shell=True)
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', doc))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(doc)
        else:                                   # linux variants
            subprocess.call(('xdg-open', doc))

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
        splash.close()
        sys.exit(app.exec_())


if __name__ == '__main__':
    main()
    
    
    
