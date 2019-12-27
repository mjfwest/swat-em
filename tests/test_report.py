# -*- coding: utf-8 -*-

import os
import shutil
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import swat_em
from swat_em.datamodel import datamodel
from swat_em.report import HtmlReport

def clean_up():
    for f in ['./report.html', 'export.txt']:
        try:
            os.remove(f)
        except:
            pass
    try:
        shutil.rmtree('report-files/')
    except:
        pass

def test_html_report():
    clean_up()
    data = datamodel()
    data.genwdg(12, 10, m=3, w=1, layers=2, turns=1)
    data.set_title('12-10 machine')
    data.set_notes('This is an example machine')

    rep = HtmlReport(data)
    #  rep.create()
    #  rep.open_in_browser()
    
    fname = rep.create('./report.html')
    print('filename:', fname)
    assert os.path.isfile('./report.html')
    clean_up()




def test_text_report():
    clean_up()
    data = datamodel()
    data.genwdg(12, 10, m=3, w=1, layers=2, turns=1)
    data.set_title('12-10 machine')
    data.set_notes('This is an example machine')
    data.export_text_report('export.txt')
    assert os.path.isfile('export.txt')
    clean_up()


if __name__ == '__main__':
    test_html_report()
    test_text_report()
