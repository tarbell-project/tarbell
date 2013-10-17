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
from .configure import tarbell_configure

class EnsureSettings():
    """Ensure the user has a Tarbell configuration."""
    def __init__(self, args):
        self.args = args
        self.path = get_config_from_args(args)

    def __enter__(self):
        if (os.path.isdir(self.path)):
            return Settings(self.path)
        else:
            puts("\n{0}: {1}".format(
                colored.red("Warning:"),
                "No Tarbell configuration found, running {0}.".format(
                    colored.green("tarbell configure")
                )
            ))
            settings = tarbell_configure(self.args)
            puts("\n\n Trying to run {0} again".format(
                colored.yellow("tarbell {0}".format(self.args.get(0)))
            ))
            return settings

    def __exit__(self, type, value, traceback):
        # @TODO This isn't quite right, __enter__ does too much work.
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

        if not os.path.exists(os.path.join(path, 'tarbell_config.py')):
            path = os.path.realpath(os.path.join(path, '..'))
            return self.ensure_site(path)
        else:
            os.chdir(path)
            site = TarbellSite(path)
            return site

# Lowercase aliases
ensure_settings = EnsureSettings
ensure_project = EnsureProject
