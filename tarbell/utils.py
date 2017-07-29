# -*- coding: utf-8 -*-

"""
tarbell.utils
~~~~~~~~~

This module provides utilities for Tarbell.
"""
from __future__ import unicode_literals
import os
import sys
from clint.textui import colored, puts as _puts

STDOUT = sys.stdout.write

def is_werkzeug_process():
    """
    Is the current process the werkzeug reloader thread? Return True if so.
    """
    return os.environ.get('WERKZEUG_RUN_MAIN') == 'true'


def puts(s='', newline=True, stream=STDOUT):
    """
    Wrap puts to avoid getting called twice by Werkzeug reloader.
    """
    if not is_werkzeug_process():
        try:
            return _puts(s, newline, stream)
        except UnicodeEncodeError:
            return _puts(s.encode(sys.stdout.encoding), newline, stream)


def list_get(l, idx, default=None):
    """
    Get from a list with an optional default value.
    """
    try:
        if l[idx]:
            return l[idx]
        else:
            return default
    except IndexError:
        return default


def split_sentences(s, pad=0):
    """
    Split sentences for formatting.
    """
    sentences = []
    for index, sentence in enumerate(s.split('. ')):
        padding = ''
        if index > 0:
            padding = ' ' * (pad + 1)
        if sentence.endswith('.'):
            sentence = sentence[:-1]
        sentences.append('%s %s.' % (padding, sentence.strip()))
    return "\n".join(sentences)


def ensure_directory(path):
    """
    Ensure directory exists for a given file path.
    """
    dirname = os.path.dirname(path)
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def show_error(msg):
    """
    Displays error message.
    """
    sys.stdout.flush()
    sys.stderr.write("\n{0!s}: {1}".format(colored.red("Error"), msg + '\n'))
