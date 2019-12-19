# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import importlib
import swat_em
importlib.reload(swat_em)

from swat_em.datamodel import datamodel
from swat_em.report import HtmlReport


data = datamodel()
data.genwdg(12, 10, m=3, w=1, layers=2, turns=1)
data.set_title('12-10 machine')
data.set_notes('This is an example machine')

rep = HtmlReport(data)
rep.create()
#  rep.open_in_browser()
