# -*- coding: utf-8 -*-

"""
legit.cli
~~~~~~~~~

This module provides the CLI interface to legit.
"""

import os
import sys
from subprocess import call
import subprocess
from time import sleep

import clint.resources
from clint import args
from clint.eng import join as eng_join
from clint.textui import colored, puts, columns

from legit.cli import cmd_switch

from .app import TarbellSite

#from .core import __version__
#from .settings import settings
#from .helpers import is_lin, is_osx, is_win
#from .scm import *

__version__ = '0.9-cli'

def black(s):
    #if settings.allow_black_foreground:
        #return colored.black(s)
    #else:
    return s.encode('utf-8')

# --------
# Dispatch
# --------

def main():
    """Primary Tarbell command dispatch."""

    command = Command.lookup(args.get(0))

    if len(args) == 0 or args.contains(('-h', '--help')):
        display_info()
        sys.exit(1)

    elif args.contains(('-v', '--version')):
        display_version()
        sys.exit(1)

    elif command:
        arg = args.get(0)
        args.remove(arg)

        command.__call__(args)
        sys.exit()

    else:
        show_error(colored.red('Unknown command {0}'.format(args.get(0))))
        display_info()
        sys.exit(1)


def first_sentence(s):
    pos = s.find('. ')
    if pos < 0:
        pos = len(s) - 1
    return s[:pos + 1]


def display_info():
    """Displays Tarbell info."""

    puts('{0}\n'.format(
        black('Tarbell: Simple web publishing'),
    ))

    puts('Usage: {0}\n'.format(colored.cyan('tarbell <command>')))
    puts('Commands:\n')
    for command in Command.all_commands():
        usage = command.usage or command.name
        help = command.help or ''
        puts('{0:35} {1}'.format(
                colored.green(usage),
                first_sentence(help)))

    puts('\n{0}'.format(
        black(u'A Chicago Tribune News Applications project')
    ))

def display_version():
    """Displays Legit version/release."""

    puts('{0} v{1}'.format(
        colored.yellow('Tarbell'),
        __version__
    ))
        

def show_error(msg):
    sys.stdout.flush()
    sys.stderr.write(msg + '\n')


def ensure_site(fn, path=None):
    def new_ensure_site(args):
        return fn(args, path)

    if not path:
        path = os.getcwd()

    if path is "/":
        show_error("The current directory is not part of a Tarbell project")
        sys.exit(1)

    if not os.path.exists(os.path.join(path, '.tarbell')):
        path = os.path.realpath(os.path.join(path, '..'))
        return ensure_site(fn, path)
    else:
        os.chdir(path)
        return new_ensure_site


@ensure_site
def tarbell_newproject(args, path):
    project = args.get(0)
    if project:
        print "@todo create new project {0}".format(project)
    else:
        show_error("No project name specified")

@ensure_site
def tarbell_serve(args, path):
    path_parts = path.split('/')
    ip = args.get(0)
    server_path = os.path.abspath(os.path.dirname(__file__))
    if not ip: ip = '127.0.0.1'
    script = "source ~/.virtualenvs/{root}/bin/activate && \
            python {server_path}/runserver.py {path} {ip}" \
            .format(root=path_parts[-1], server_path=server_path, path=path, ip=ip)
    process = subprocess.Popen(["/bin/bash"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, stderr = process.communicate(script)
    print stdout
    print stderr

def tarbell_switch(args):
    cmd_switch(args)    # legit switch
    tarbell_serve(args) # serve 'em up!


class Command(object):
    COMMANDS = {}
    SHORT_MAP = {}

    @classmethod
    def register(klass, command):
        klass.COMMANDS[command.name] = command
        if command.short:
            for short in command.short:
                klass.SHORT_MAP[short] = command

    @classmethod
    def lookup(klass, name):
        if name in klass.SHORT_MAP:
            return klass.SHORT_MAP[name]
        if name in klass.COMMANDS:
            return klass.COMMANDS[name]
        else:
            return None

    @classmethod
    def all_commands(klass):
        return sorted(klass.COMMANDS.values(),
                      key=lambda cmd: cmd.name)

    def __init__(self, name=None, short=None, fn=None, usage=None, help=None):
        self.name = name
        self.short = short
        self.fn = fn
        self.usage = usage
        self.help = help

    def __call__(self, *args, **kw_args):
        return self.fn(*args, **kw_args)


def def_cmd(name=None, short=None, fn=None, usage=None, help=None):
    command = Command(name=name, short=short, fn=fn, usage=usage, help=help)
    Command.register(command)


def_cmd(
    name='newproject',
    fn=tarbell_newproject,
    usage='newproject <project>',
    help='Create a new project named <project>')


def_cmd(
    name='serve',
    fn=tarbell_serve,
    usage='serve',
    help='Run a preview server (typically handled by `switch`)')


def_cmd(
    name='switch',
    fn=tarbell_switch,
    usage='switch <project>',
    help='Switch to the project named <project> and start a preview server.')
