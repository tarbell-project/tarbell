# -*- coding: utf-8 -*-

"""
tarbell.cli
~~~~~~~~~

This module provides context managers for Tarbell projects.
"""

import os
import sys

from clint.textui import colored, puts

from .app import TarbellSite
from .settings import Settings
from .utils import show_error, get_config_from_args


class EnsureSettings():
    """Ensure the user has a Tarbell configuration."""
    def __init__(self, args):
        self.args = args
        self.path = get_config_from_args(args)

    def __enter__(self):
        if (os.path.isdir(self.path)):
            return Settings(self.path)
        else:
            puts(colored.red("-- No Tarbell configuration found, configuring Tarbell. --\n"))
            tarbell_configure(self.args)

    def __exit__(self, type, value, traceback):
        pass


class EnsureProject():
    """Context manager to ensure the user is in a Tarbell site environment."""
    def __init__(self, args):
        self.args = args

    def __enter__(self):
        return self.ensure_site()

    def __exit__(self, type, value, traceback):
        pass

    def ensure_site(self, path=None):
        if not path:
            path = os.getcwd()

        if path is "/":
            show_error(("The current directory is not part of a Tarbell "
                        "project"))
            sys.exit(1)

        if not os.path.exists(os.path.join(path, 'tarbell.py')):
            path = os.path.realpath(os.path.join(path, '..'))
            return self.ensure_site(path)
        else:
            os.chdir(path)
            with ensure_settings(self.args) as settings:
                site = TarbellSite(path, settings.path)
                puts("Activating {0} ({1})\n".format(
                        colored.red(site.project.TITLE),
                        colored.yellow(site.project.NAME)
                    ))
                return site

# Lowercase aliases
ensure_settings = EnsureSettings
ensure_project = EnsureProject
