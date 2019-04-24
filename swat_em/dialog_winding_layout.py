from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QMessageBox
from swat_em.config import get_phase_color
import os
__dir__ = os.path.dirname(os.path.abspath(__file__))
#  import numpy as np

class layout(QDialog):
    '''
    This is a basic winding editor to define and change the 
    winding layout
    '''
    def __init__(self, data):
        self.data = data
        super().__init__()
        # Set up the user interface from Designer.
        uic.loadUi(os.path.join(__dir__, 'ui/winding_layout.ui'), self)
        self.setWindowTitle('Edit winding layout')
        
        self.Button_EditMachineData.clicked.connect(self.dialog_machinedata)
        
        #  self.Button_CANCEL.clicked.connect(self.reject)
        #  self.Button_OK.clicked.connect(self.accept)
        
        
        self.tableWindingLayout.cellChanged.connect(self.update_colors)
        self.update_table(self.data.machinedata['phases'])

        self.update_lineEdits(self.data.machinedata['Q'],
                              self.data.machinedata['m'],
                              2*self.data.machinedata['p'],
                              self.data.get_num_layers()
                              )
        
    
    def dialog_machinedata(self):
        '''
        User can change Q, m, P, layers
        '''
        dialog = machinedata(self.data)
        ret = dialog.run()   
        make_update = False
        if ret:
            if ret['Q'] != self.data.machinedata['Q']:
                make_update = True
            if ret['layers'] != self.data.get_num_layers():
                make_update = True
                for km in range(len(self.data.machinedata['phases'])):
                    for ks in range(1, len(self.data.machinedata['phases'][km])):
                        self.data.machinedata['phases'][km][ks] = []
            self.data.set_machinedata(Q = ret['Q'], m = ret['m'], p = ret['P']/2)
            self.update_lineEdits(self.data.machinedata['Q'],
                              self.data.machinedata['m'],
                              2*self.data.machinedata['p'],
                              ret['layers']
                              )
            if make_update:
                self.update_table(self.data.machinedata['phases'], layers=ret['layers'])
            
                
    
        
    def update_lineEdits(self, Q, m, P, layers):
        self.lineEdit_Q.setText(str(Q))
        self.lineEdit_m.setText(str(m))
        self.lineEdit_P.setText(str(P))
        if layers == 1:
            self.radioButton_slayer.setChecked(True)
        else:
            self.radioButton_dlayer.setChecked(True)



    def update_table(self, phases, layers = None):
        self.table = self.tableWindingLayout        
        self.table.setColumnCount(self.data.machinedata['Q'])        
        
        head = ['Layer 1', 'Layer 2']
        if not layers:
            layers = self.data.get_num_layers()
        self.table.setRowCount(layers)
        self.table.setVerticalHeaderLabels(head[:layers])

     
        for km, ph in enumerate(phases):
            col = get_phase_color(self.data.config, km)
            for kl in range(len(ph)):
                layer = ph[kl]
                for cs in layer:
                    if cs > 0:
                        self.table.setItem(kl, cs-1, QTableWidgetItem('+' + str(km+1)))
                    else:
                        self.table.setItem(kl, abs(cs)-1, QTableWidgetItem('-' + str(km+1)))
                    item = self.table.item(kl, abs(cs)-1)
                    if item:
                        item.setBackground(QtGui.QColor(col))

        for k1 in range(self.data.machinedata['Q']):
            self.table.resizeColumnToContents(k1)


        #  self.table.setHorizontalHeaderLabels(['nu'] + self.data.machinedata['phasenames'])
        #  self.table.setVerticalHeaderLabels(['']*np.shape(kw)[0])
        #  afont = QFont()
        #  afont.setBold(True)
        
        #  for k in range(self.data.machinedata['m'] + 1):
            #  self.table.horizontalHeaderItem(k).setFont(afont)
    
    
    
    def read_layout(self):
        '''
        Read layout from table
        '''
        S = []
        for layer in [0, 1]:
            for k in range(self.data.machinedata['Q']):
                item = self.table.item(layer, k)
                if item:
                    txt = str(item.text())
                    phase = int(txt)
                    sign = 1 if phase > 0 else -1
                    while len(S) < abs(phase):
                        S.append([[],[]])
                    S[abs(phase)-1][layer].append( (k+1)*sign )
        return S
        

    def update_colors(self):
        '''
        Update the colors in the table if the user defines phases here
        Also there are some tests for the winding
        '''
        error = []
        warning = []
        
        for layer in [0, 1]:
            for k in range(self.data.machinedata['Q']):
                item = self.table.item(layer, k)
                if item:
                    txt = str(item.text())
                    phase = abs(int(txt))
                    col = get_phase_color(self.data.config, phase-1)
                    item.setBackground(QtGui.QColor(col))
        
        # Test for errors
        S = self.read_layout()        
        for k in range(len(S)):
            S[k] = [item for sublist in S[k] for item in sublist]  # flatten layers
        
        # test if the number of positve and negative coil sides are equal
        for k in range(len(S)):
            s = S[k]
            pos = 0; neg = 0
            for w in s:
                if w > 0:
                    pos += 1
                elif w < 0:
                    neg += 1
            if pos != neg:
                error.append('Phase {} has {} postive and {} negative coil sides'.format(k+1, pos, neg))

        # test if all phases have the same number of coil sides
        l = [len(s) for s in S]
        if len(set(l)) != 1:
            txt = 'Not all phases have the same number of coil sides:<br>'            
            for k in range(len(S)):
                txt += 'Phase {} hat {} coilsides<br>'.format(k+1, l[k])
            error.append(txt)

        if len(S) > self.data.machinedata['m']:
            error.append('There are {} phases but in main window only m = {} is set'.format(
                len(S), self.data.machinedata['m']))

        # print errors
        txt_error = '<span style=\" color:#ff0000;\" >'
        for e in error:
            txt_error += str(e) + '<br>'
        txt_error += '</span>'
        self.textBrowser_output.setHtml(txt_error)


        
    def run(self):
        ok = self.exec_()
        if ok:
            phases = self.read_layout()
            layer1 = False; layer2 = False  # test if single or double layer winding
            for s in phases:
                if len(s[0]) > 0:
                    layer1 = True
                if len(s[1]) > 0:
                    layer2 = True
            if layer1 and layer2:
                layers = 2
            else:
                layers = 1
            
            Q = self.data.machinedata['Q']
            p = self.data.machinedata['p']
            m = self.data.machinedata['m']
            w = self.data.machinedata['wstep']       
            ret = {'phases': phases, 'Q': Q, 'P': 2*p, 'm': m, 'w': w, 'layers': layers}
            return ret
        else:
            return None
        

        
        
        

        
    



class machinedata(QDialog):
    '''
    User can change Q, m, P, layers
    '''
    def __init__(self, data):
        self.data = data
        super().__init__()
        uic.loadUi(os.path.join(__dir__, 'ui/MachineData.ui'), self)
        self.setWindowTitle('Change machine data')
        self.data = data
        self.spinBox_Q.setValue(self.data.machinedata['Q'])
        self.spinBox_m.setValue(self.data.machinedata['m'])
        self.spinBox_P.setValue(2*self.data.machinedata['p'])
        if self.data.get_num_layers() == 1:
            self.radioButton_slayer.setChecked(True)
        else:
            self.radioButton_dlayer.setChecked(True)
        

    def run(self):
        ok = self.exec_()
        if ok:
            if self.radioButton_slayer.isChecked():
                layers = 1
            elif self.radioButton_dlayer.isChecked():
                layers = 2
            Q = self.spinBox_Q.value()
            P = self.spinBox_P.value()
            m = self.spinBox_m.value()
            if Q < self.data.machinedata['Q']:
                buttonReply = QMessageBox.question(self, 'Warning',
                 '''The defined number of slots is lower than the number of slots in the actual winding. \
Is it ok to loose some these informations of the actual winding layout?''', 
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if buttonReply != QMessageBox.Yes:
                    return None
            
            if layers < self.data.get_num_layers():
                buttonReply = QMessageBox.question(self, 'Warning',
                 '''The defined number of layers is lower than the number of layers in the actual winding. \
Is it ok to loose some these informations of the actual winding layout?''', 
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if buttonReply != QMessageBox.Yes:
                    return None
            
            ret = {'Q': Q, 'P': P, 'm': m, 'layers': layers}
            return ret
        else:
            return None









