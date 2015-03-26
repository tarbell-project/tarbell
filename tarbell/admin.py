# -*- coding: utf-8 -*-

"""
tarbell.admin
~~~~~~~~~

This module provides admin utilities for Tarbell cli and gui.
"""
import sys
import imp
import os

def load_module_dict(module_name, module_path):
    """
    Load module as a dictionary
    This works fine as long as the module doesn't import other modules!
    """
    filename, pathname, description = imp.find_module(module_name, [module_path])
    m = imp.load_module(os.path.dirname(module_path), filename, pathname, description)
    
    d = dict([(varname, getattr(m, varname)) \
        for varname in dir(m) if not varname.startswith("_") ]) 

    del sys.modules[m.__name__]
    return d

def list_projects(projects_dir):
    """Get a list of projects"""
    projects_list = []

    for directory in os.listdir(projects_dir):
        project_path = os.path.join(projects_dir, directory)
        try:
            config = load_module_dict('tarbell_config', project_path)
            title = config.get('DEFAULT_CONTEXT').get("title", directory)
            projects_list.append({'directory': directory, 'title': title})
        except ImportError:
            pass
    
    return projects_list
