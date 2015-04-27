# -*- coding: utf-8 -*-

"""
tarbell.admin
~~~~~~~~~

This module provides admin utilities for Tarbell cli and gui.
"""
import getpass
import httplib2
import imp
import os
import shutil
import sys
import yaml

from datetime import datetime
from clint.textui import colored

from oauth2client import client
from oauth2client import keyring_storage

from .oauth import OAUTH_SCOPE
from .utils import puts


DEFAULT_BLUEPRINTS = [
    {
        "name": "Basic Bootstrap 3 template",
        "url": "https://github.com/newsapps/tarbell-template",
    }, 
    {
        "name": "Searchable map template",
        "url": "https://github.com/eads/tarbell-map-template",
    },
    {
        "name": "Tarbell template walkthrough",
        "url": "https://github.com/hbillings/tarbell-tutorial-template",
    },
    {
        "name": "Empty project (no blueprint)"
    }
]  


def props(obj):
    """
    Return object as dictionary
    Only gets attributes set on the instance, not on the class!
    """
    return dict((key, value) \
        for key, value in obj.__dict__.iteritems() \
        if not callable(value) and not key.startswith('__'))

def backup(path, filename):
    """Backup a file"""
    target = os.path.join(path, filename)
    if os.path.isfile(target):
        dt = datetime.now()
        new_filename = ".{0}.{1}.{2}".format(
            filename, dt.isoformat(), "backup"
        )
        destination = os.path.join(path, new_filename)
        print("- Backing up {0} to {1}".format(
            colored.cyan(target),
            colored.cyan(destination)
        ))
        shutil.copy(target, destination)

def safe_write(data, path, backup_existing=True):
    """Write data to path.  If path exists, backup first"""
    dirname = os.path.dirname(path)
    filename = os.path.basename(path)
    
    if backup_existing and os.path.exists(path):
        backup(dirname, filename)
    
    print 'Writing %s' % path
    with open(path, 'w+') as f:
        f.write(data)
         
def get_or_create_config(path):
    """Get or create a tarbell configuration directory"""
    dirname = os.path.dirname(path)
    filename = os.path.basename(path)

    try:
        os.makedirs(dirname)
    except OSError:
        pass

    try:
        with open(path, 'r+') as f:
            if os.path.isfile(path):
                puts("{0} already exists, backing up".format(colored.green(path)))
                backup(dirname, filename)
            return yaml.load(f)
    except IOError:
        return {}
    
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

    path_prefix = os.path.expanduser(projects_dir)
    for directory in os.listdir(path_prefix):
        project_path = os.path.join(path_prefix, directory)
        try:
            config = load_module_dict('tarbell_config', project_path)
            title = config.get('DEFAULT_CONTEXT').get("title", directory)
            projects_list.append({'directory': directory, 'title': title})
        except ImportError:
            pass
    
    return projects_list

def client_secrets_authorize_url(client_secrets_path):  
    """Get the client_secrets authorization url"""
    flow = client.flow_from_clientsecrets(client_secrets_path, \
        scope=OAUTH_SCOPE, redirect_uri=client.OOB_CALLBACK_URN)
    return flow.step1_get_authorize_url()

def client_secrets_authorize(client_secrets_path, code):
    """Authorize client_secrets"""
    flow = client.flow_from_clientsecrets(client_secrets_path, \
        scope=OAUTH_SCOPE, redirect_uri=client.OOB_CALLBACK_URN)

    try:
        storage = keyring_storage.Storage('tarbell', getpass.getuser())
        credentials = flow.step2_exchange(code, http=httplib2.Http())
        storage.put(credentials)        
    except client.FlowExchangeError, e:
        raise Exception('Authentication failed: %s' % e)    
