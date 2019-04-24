# -*- coding: utf-8 -*-
'''
Provides the config and the handling of it
''' 
import copy
import os
import sys
import json


def get_config_dir():
    '''
    Returns the configuration dictionary of the user

    Returns
    -------
    return : string
             config folder
             LINUX / OSX: ~/.config/swat-em/
             WINSOWS: ../appdata/swat-em/
    '''
    if 'linux' in sys.platform:
        user_config_dir = os.path.join(os.path.expanduser("~"), '.config/swat-em')
    elif 'darwin' in sys.platform:
        user_config_dir = os.path.join(os.path.expanduser("~"), '.config/swat-em')
    else:
        user_config_dir = os.path.join(os.getenv("APPDATA"), 'swat-em')
    return user_config_dir


def get_init_config():
    config = {}
    config['N_nu_el'] = 19
    config['N_nu_mech'] = 19
    config['max_nu_MMK'] = 19
    config['kw_min'] = 0.01

    config['plt'] = {
                     'lw': 2.0,
                     'lw_thin': 1.0,
                     'DPI': 90,
                     'phase_colors': ['#1b9e77','#d95f02','#7570b3',
                     '#e7298a','#66a61e','#e6ab02','#a6761d'] # http://colorbrewer2.org/#type=qualitative&scheme=Dark2&n=7
                     }                     
    return copy.deepcopy(config)


def get_phase_color(config, num):
    cols = config['plt']['phase_colors']
    while num > len(cols):
        num -= len(cols)    # periodic colors
    return cols[num]


def get_config(default = True):
    '''
    Returns the configuration dictionary
    
    Parameters
    ----------
    default : Boolean
              if True:  returns the default config
              if False: returns the config from the home-directory of the user
             
    Returns
    -------
    return : dictionary
             config dict
    '''
    if default:
        return get_init_config()
    else:
        config = load_config()
        if config:
            return config
        else:
            return get_init_config()


def save_config(config):
    '''
    Saves the configuration in the home directory of the user
    
    Parameters
    ----------
    config : Dictionary
             config dict
    '''
    user_config_dir = get_config_dir()
    if not os.path.isdir(user_config_dir):
        os.mkdir(user_config_dir)
    with open(os.path.join(user_config_dir, 'config.json'), 'w') as f:
        json.dump(config, f, indent = 2)


def load_config():
    '''
    Saves the configuration in the home directory of the user
    
    Returns
    -------
    return : dictionary
             config dict from user home directory. Use default config
             if there is no config file of the user
    '''
    user_config_dir = get_config_dir()
    if not os.path.isdir(user_config_dir):
        os.mkdir(user_config_dir)

    if os.path.isfile(os.path.join(user_config_dir, 'config.json')):
        with open(os.path.join(user_config_dir, 'config.json')) as f:
            config = json.load(f)
            # test for new data
            config_init = get_init_config()
            for key, value in config_init.items():
                if key not in config.keys():
                    config[key] = value
            for key, value in config_init['plt'].items():
                if key not in config['plt'].keys():
                    config['plt'][key] = value
    else:
        return get_init_config()        
    return config




    
