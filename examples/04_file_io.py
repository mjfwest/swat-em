# -*- coding: utf-8 -*-
# 04_file_io.py - Load/save windings for exchange with the gui
#                 exporting reports

from swat_em import datamodel


wdg = datamodel()
wdg.genwdg(Q=12, P=2, m=3, layers=1)

# Save to a *.wdg file. This file can be used with the GUI for example.
# swat-em uses the 'json' format for the *.wdg files.
print("export to wdg file")
wdg.save_to_file("myfile.wdg")

# Load a *.wdg file
wdg2 = datamodel()
wdg2.load_from_file("myfile.wdg")

# proof, that the data of the two objects is equal:
print("same data?:", wdg.machinedata == wdg2.machinedata)
print("same results?:", wdg.results == wdg2.results)


# export data to Excel xlsx files:
wdg.export_xlsx("export.xlsx")


# Generate a text report of the winding
wdg.export_text_report("report.txt")


# Generate a html report with figures of the winding
wdg.export_html_report("report.html")
