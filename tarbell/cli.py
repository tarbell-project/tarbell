# -*- coding: utf-8 -*-

"""
tarbell.cli
~~~~~~~~~

This module provides the CLI interface to tarbell.
"""

import os
import sys
from subprocess import call

from clint import args
from clint.textui import colored, puts

from legit.cli import cmd_switch, cmd_branches

import tempfile
import shutil

from .app import TarbellSite
from .oauth import get_drive_api

__version__ = '0.9'


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


class EnsureSite():
    """Context manager to ensure the user is in a Tarbell site environment."""
    def __init__(self, reset=False):
        self.reset = reset

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
            self.ensure_secrets(path)
            return path

    def ensure_secrets(self, path):
        # Check for client secrets? Might be unnecessary, really.
        client = get_drive_api(path, self.reset)
        # Trap errors and show docs

# Alias to lowercase
ensure_site = EnsureSite


# --------
# Dispatch
# --------
def main():
    """Primary Tarbell command dispatch."""

    command = Command.lookup(args.get(0))

    if len(args) == 0 or args.contains(('-h', '--help', 'help')):
        display_info()
        sys.exit(1)

    elif args.contains(('-v', '--version')):
        display_version()
        sys.exit(1)

    elif command:
        arg = args.get(0)
        args.remove(arg)

        reset = False
        if args.contains('--reset-creds'):
            reset = True
            args.remove('--reset-creds')

        with ensure_site(reset) as path:
            command.__call__(args, path)

        sys.exit()

    else:
        show_error(colored.red('Error! Unknown command `{0}`.\n'.format(args.get(0))))
        display_info()
        sys.exit(1)


def split_sentences(s):
    """Split sentences for formatting."""
    sentences = []
    for index, sentence in enumerate(s.split('. ')):
        pad = ''
        if index > 0:
            pad = ' ' * 39
        if sentence.endswith('.'):
            sentence = sentence[:-1]
        sentences.append('%s %s.' % (pad, sentence.strip()))
    return "\n".join(sentences)


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
        puts('{0:48} {1}\n'.format(
                colored.green(usage),
                split_sentences(help)))

    puts('\nOptions\n')
    puts('{0:48} {1}'.format(
        colored.green("--reset-creds"),
        'Reset Google Drive OAuth2 credentials'
    ))

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
    """Displays error message."""
    sys.stdout.flush()
    sys.stderr.write("{0}: {1}".format(colored.red("Error"), msg + '\n'))


def tarbell_generate(args, path):
    """Generate static files."""
    site = TarbellSite(path)
    output_root = list_get(args, 0, False)
    if not output_root:
        tempdir = tempfile.mkdtemp(prefix="{0}-".format(site.project.__name__))
        os.makedirs(os.path.join(tempdir, site.project.__name__))
        output_root = os.path.join(tempdir, site.project.__name__)
    else:
        tempdir = output_root
        output_root = os.path.join(tempdir, site.project.__name__)
    site.generate_static_site(output_root)
    puts("\nCreated site in {0}".format(output_root))
    return tempdir


def tarbell_list(args, path):
    """List tarbell projects."""
    cmd_branches(path)


def tarbell_publish(args, path):
    """Publish a site by calling s3cmd"""
    site = TarbellSite(path)
    bucket_name = list_get(args, 0, "staging")
    bucket_uri = site.project.S3_BUCKETS.get(bucket_name, False)

    try:
        if bucket_uri:
            puts("Deploying to {0} ({1})\n".format(
                colored.green(bucket_name), colored.green(bucket_uri)))
            tempdir = tarbell_generate([], path)
            projectdir = os.path.join(tempdir, site.project.__name__)
            call(['s3cmd', 'sync', '--acl-public', '--delete-removed',
                  projectdir, bucket_uri])
        else:
            show_error(("There's no bucket configuration called '{0}' "
                        "in config.py.\n".format(bucket_name)))
    except KeyboardInterrupt:
        show_error("ctrl-c pressed, bailing out!")
    finally:
        # Delete tempdir
        try:
            shutil.rmtree(tempdir)  # delete directory
            puts("\nDeleted {0}".format(tempdir))
        except OSError as exc:
            if exc.errno != 2:  # code 2 - no such file or directory
                raise  # re-raise exception
        except UnboundLocalError:
            pass


def tarbell_newproject(args, path):
    """Create new Tarbell project."""
    project = args.get(0)
    if project:
        print "@todo create new project {0}".format(project)
    else:
        show_error("No project name specified")


def tarbell_serve(args, path):
    """Serve the current Tarbell project."""
    address = list_get(args, 0, "").split(":")
    ip = list_get(address, 0, '127.0.0.1')
    port = list_get(address, 1, 5000)
    site = TarbellSite(path)
    site.app.run(ip, port=int(port))


def tarbell_switch(args, path):
    """Switch to a project"""
    cmd_switch(args)               # legit switch
    tarbell_serve(args[1:], path)  # serve 'em up!


def tarbell_unpublish(args, path):
    """Delete a project."""
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
    """Define a command."""
    command = Command(name=name, short=short, fn=fn, usage=usage, help=help)
    Command.register(command)


def_cmd(
    name='generate',
    fn=tarbell_generate,
    usage='generate <output dir (optional)>',
    help=('Generate static files for the current project. If no output '
          'directory is specified, create a temporary directory.'))


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
    name='serve',
    fn=tarbell_serve,
    usage='serve <address (optional)>',
    help=('Run a preview server (typically handled by `switch`). '
          'Supply an optional address for the preview server such as '
          '`127.0.0.2:8000`'))


def_cmd(
    name='switch',
    fn=tarbell_switch,
    usage='switch <project> <address (optional)>',
    help=('Switch to the project named <project> and start a preview server. '
          'Supply an optional address for the preview server such as '
          '`127.0.0.2:8000`'))


def_cmd(
    name='unpublish',
    fn=tarbell_unpublish,
    usage='unpublish <target (default: staging)>',
    help='Remove the current project from <target>.')
