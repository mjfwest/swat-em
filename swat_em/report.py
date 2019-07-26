# -*- coding: utf-8 -*-
'''
Provides functions for reports
''' 

def italic(txt):
    return '<i>' + txt + '</i>'


def table_header(data):
    txt = ['<tr>']
    for d in data:
        txt.append('<th>')
        txt.append(d)
        txt.append('</th>')
    txt.append('</tr>')
    return ''.join(txt)


def table_row(data, col = None):
    if col:
        txt = ['<tr bgcolor="{}">'.format(col)]
    else:
        txt = ['<tr>']
    for d in data:
        txt.append('<td>')
        txt.append(d)
        txt.append('</td>')
    txt.append('</tr>')
    return ''.join(txt)


def red(text):
    txt = ['<span style=\" color:#ff0000;\" >']
    txt.append(text)
    txt.append('</span>')
    return ''.join(txt)


def table(dat):
    txt = ['<table style="width:100%">']
    col1 = '#FFFFFF'
    col2 = '#CBCBCB'
    for i, d in enumerate(dat):
        col = col1 if i%2 != 0 else col2
        txt.append(table_row(d, col=col))
    
    txt.append('</table>')
    return txt
