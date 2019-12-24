# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from swat_em.wdggenerator import genwdg
from swat_em.datamodel import datamodel
from swat_em.config import config, get_phase_color





data = datamodel()
data.set_title('Q = 12, 2p = 10')
data.set_notes('Example winding')
data.genwdg(Q = 12, P = 10, m = 3, w = 1, layers = 2)
data.analyse_wdg()
bc, txt = data.get_basic_characteristics()
#  data.export_xlsx('export.xlsx')


data.export_text_report('export.txt')




#  import os
#  os.system('loffice export.xlsx')
