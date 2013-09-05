# -*- coding: utf-8 -*-

"""
tarbell.cli
~~~~~~~~~

This module provides the CLI interface to tarbell.
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

__version__ = '0.9'

def list_get(l, idx, default=None):
    try:
        if l[idx]:
            return l[idx]
        else:
            return default
    except IndexError:
        return default

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
        puts('{0:50} {1}'.format(
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
def tarbell_list(args, path):
    print "@todo list projects"


@ensure_site
def tarbell_publish(args, path):
    print "@todo publish"


@ensure_site
def tarbell_newproject(args, path):
    project = args.get(0)
    if project:
        print "@todo create new project {0}".format(project)
    else:
        show_error("No project name specified")

@ensure_site
def tarbell_serve(args, path):
    address = list_get(args, 0, "").split(":")
    ip = list_get(address, 0, '127.0.0.1')
    port = list_get(address, 1, 5000)
    site = TarbellSite(path)
    site.app.run(ip, port=int(port))


@ensure_site
def tarbell_stop(args, path):
    print "@todo stop server"


@ensure_site
def tarbell_switch(args, path):
    cmd_switch(args)        # legit switch
    tarbell_serve(args[1:]) # serve 'em up!


@ensure_site
def tarbell_unpublish(args, path):
    print "@todo unpublish"


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
    name='list',
    fn=tarbell_list,
    usage='list',
    help='List all projects.')


def_cmd(
    name='publish',
    fn=tarbell_publish,
    usage='publish <target (default: staging)>',
    help='Publish the current project to <target>.')


def_cmd(
    name='newproject',
    fn=tarbell_newproject,
    usage='newproject <project>',
    help='Create a new project named <project>')


def_cmd(
    name='serve <address (optional)>',
    fn=tarbell_serve,
    usage='serve',
    help='Run a preview server (typically handled by `switch`)')


def_cmd(
    name='stop',
    fn=tarbell_stop,
    usage='stop',
    help='Stop a running preview server.')


def_cmd(
    name='switch',
    fn=tarbell_switch,
    usage='switch <project> <address (optional)>',
    help='Switch to the project named <project> and start a preview server.')


def_cmd(
    name='unpublish',
    fn=tarbell_unpublish,
    usage='unpublish <target (default: staging)>',
    help='Remove the current project from <target>.')


