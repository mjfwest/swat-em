from PyQt5 import uic
from PyQt5.QtWidgets import QDialog
import os
__dir__ = os.path.dirname(os.path.abspath(__file__))
import swat_em

class about(QDialog):
    def __init__(self):
        super().__init__()
        # Set up the user interface from Designer.
        uic.loadUi(os.path.join(__dir__, 'ui/About.ui'), self)
        self.Button_close.clicked.connect(self.close)
        
        txt = self.textBrowser.toHtml()   
        txt = txt.replace('%1%', swat_em.__version__) # placeholder in Qt Designer
        self.textBrowser.setHtml(txt)
        
        self.exec_()

        
    
