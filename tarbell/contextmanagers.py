# -*- coding: utf-8 -*-

"""
tarbell.cli
~~~~~~~~~

This module provides context managers for Tarbell projects.
"""

import os

from .app import TarbellSite
from .settings import Settings


class EnsureSettings():
    """Ensure the user has a Tarbell configuration."""
    def __init__(self, args):
        self.args = args

    def __enter__(self):
        #tarbell_configure(self.args)
        return Settings()

    def __exit__(self, type, value, traceback):
        pass

ensure_settings = EnsureSettings

class EnsureSite():
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

        if not os.path.exists(os.path.join(path, '.tarbell')):
            path = os.path.realpath(os.path.join(path, '..'))
            return self.ensure_site(path)
        else:
            os.chdir(path)
            return TarbellSite(path)

ensure_site = EnsureSite
