Getting Results
===============
After generating a winding, swat-em analyze it and provides the results:

.. code-block:: python

    >>> wdg = datamodel()
    >>> wdg.genwdg(Q = 12, P = 2, m = 3, layers = 1) 
    >>> print('fundamental winding factor: ', wdg.get_fundamental_windingfactor())
    fundamental winding factor:  [0.9659258262890683, 0.9659258262890683, 0.9659258262890684]
    >>> print('winding step: ', wdg.get_windingstep())
    winding step:  6




Get the generated winding layout:
For each phase there is a list of the 1st and 
the 2nd layer. In this example there is only 1 layer, so the second
list is empty. An entry of the lists define the slot number in which
is a coil-side of the phase is located. A negative number means, that 
the winding direction is reversed in the slot.

.. code-block:: python

    >>> print('winding layout:', wdg.get_phases())
    winding layout: [[[1, 2, -7, -8], []], [[5, 6, -11, -12], []], [[-3, -4, 9, 10], []]]


The winding factor depends on the harmonic number. There are two 
possible interpretations for the harmonic number: The 'electrical'
harmonic numbers the 'mechanical' ordinal numbers multiplyed with
number of pole pairs 'p'. Use the 'mechanical' winding factor if you
want du determine the possible number of poles your winding can drive
and use the electrical winding factor if you know your number of pole
pairs and if you want to analyze the harmonic content of the winding
for example.
Attention: The winding factor is calculated for each phase seperately.

.. code-block:: python

    >>> nu, kw = wdg.get_windingfactor_el()
    >>> for k in range(len(nu)):
    >>>     print(nu[k], kw[k])
    1 [0.96592583 0.96592583 0.96592583]
    3 [-0.70710678 -0.70710678 -0.70710678]
    5 [-0.25881905 -0.25881905 -0.25881905]
    7 [0.25881905 0.25881905 0.25881905]
    9 [-0.70710678 -0.70710678 -0.70710678]
    ...




The datamodel() object stores the data in dictionaries. The user 
have direct access:

.. code-block:: python

    >>> print('Data for the machine: ', wdg.machinedata.keys())
    Data for the machine:  dict_keys(['Q', 'p', 'm', 'phases', 'wstep', 'turns', 'phasenames'])
    >>> # ... and all results:
    >>> print('Data for the machine: ', wdg.results.keys())
    Data for the machine:  dict_keys(['q', 'nu_el', 'Ei_el', 'kw_el', 'phaseangle_el', 'nu_mech', 'Ei_mech', 'kw_mech', 'phaseangle_mech', 'valid', 'error', 't', 'wdg_is_symmetric', 'wdg_periodic', 'MMK', 'basic_char'])


For getting the results the get_* methods can be used:

.. code-block:: python

    >>> print('Is winding symmetric:', wdg.get_is_symmetric())
    Is winding symmetric: True
    >>> print('Fundamental winding factor:', wdg.get_fundamental_windingfactor())
    Fundamental winding factor: [0.9659258262890683, 0.9659258262890683, 0.9659258262890684]
    >>> print('Number of turns in series:', wdg.get_num_series_turns())
    Number of turns in series: 2.0
    >>> print('Excited radial force modes:', wdg.get_radial_force_modes())
    Excited radial force modes: [2, 4, 6]
    >>> print('Periodictiy:', wdg.get_periodicity_t())
    Periodictiy: 1
    >>> print('Possible parallel connections:', wdg.get_parallel_connections())
    Possible parallel connections: [1, 2]
    >>> print('Double linked leakage:', wdg.get_double_linked_leakage())
    Double linked leakage: 0.02843683350047214





