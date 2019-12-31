File IO
=======

Save/load a winding
-------------------

After creating a winding we can save it as a \*.wdg file
This file can be used with the GUI for example.
swat-em uses the "json" format for the \*.wdg files.

.. code-block:: python

    >>> wdg = datamodel()
    >>> wdg.genwdg(Q = 12, P = 2, m = 3, layers = 1) 
    >>> wdg.save_to_file('myfile.wdg')


We can also load an existing winding from file:

.. code-block:: python

    >>> wdg2 = datamodel()


Proof, that the data of the two objects is equal:

.. code-block:: python

    >>> print('same data?:', wdg.machinedata == wdg2.machinedata)
    same data?: True
    >>> print('same results?:', wdg.results == wdg2.results)
    same results?: True


Export to Excel file
--------------------

The data of an existing winding can exported to an Excel file (\*.xlsx).
Attention: The old \*.xls format is not supported!

.. code-block:: python

    >>> wdg.export_xlsx('export.xlsx')


Text report
-----------

A summary of the winding can be exported as a text report:

.. code-block:: python

    >>> wdg.export_text_report('report.txt')


HTML report
-----------

Similar to the text report we can create a html report. 
This also includes the graphics.

.. code-block:: python

    >>> wdg.export_html_report('report.html')







