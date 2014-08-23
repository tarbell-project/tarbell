# -*- coding: utf-8 -*-

"""
tarbell.utils
~~~~~~~~~

This module provides utilities for Tarbell.
"""

import os
import sys
from clint.textui import colored


def list_get(l, idx, default=None):
    """Get from a list with an optional default value."""
    try:
        if l[idx]:
            return l[idx]
        else:
            return default
    except IndexError:
        return default


def black(s):
    """Black text."""
    #if settings.allow_black_foreground:
        #return colored.black(s)
    #else:
    return s.encode('utf-8')


def split_sentences(s, pad=0):
    """Split sentences for formatting."""
    sentences = []
    for index, sentence in enumerate(s.split('. ')):
        padding = ''
        if index > 0:
            padding = ' ' * (pad + 1)
        if sentence.endswith('.'):
            sentence = sentence[:-1]
        sentences.append('%s %s.' % (padding, sentence.strip()))
    return "\n".join(sentences)


def show_error(msg):
    """Displays error message."""
    sys.stdout.flush()
    sys.stderr.write("\n{0}: {1}".format(colored.red("Error"), msg + '\n'))


def get_config_from_args(args):
    """Get config directory from arguments."""
    return os.path.expanduser(
        os.path.join("~", ".{0}".format("tarbell"), "settings.yaml")
    )
    return path


def filter_files(path):
    for dirpath, dirnames, filenames in os.walk(path):
        dirnames[:] = [
            dn for dn in dirnames
            if not dn.startswith('.') and not dn.startswith('_')
        ]
        filenames[:] = [
            fn for fn in filenames
            if not fn.endswith('.py') and not fn.endswith('.pyc') and not fn.startswith('.') and not fn.startswith('_')
        ]
        yield dirpath, dirnames, filenames
