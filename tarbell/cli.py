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
from clint.arguments import Args
from clint.textui import colored, puts

import jinja2
import codecs
import mimetypes

import tempfile
import shutil

from apiclient import errors
from apiclient.http import MediaFileUpload as _MediaFileUpload
from oauth2client.clientsecrets import InvalidClientSecretsError

from git import Repo

from .oauth import get_drive_api
from .contextmanagers import ensure_settings, ensure_site
from .configure import tarbell_configure
from .utils import list_get, black, split_sentences, show_error

__version__ = '0.9'

from jinja2.loaders import BaseLoader
from .utils import filter_files

class TarbellFileSystemLoader(BaseLoader):
    """Loads templates from the file system.  This loader can find templates
    in folders on the file system and is the preferred way to load them.

    The loader takes the path to the templates as string, or if multiple
    locations are wanted a list of them which is then looked up in the
    given order:

    >>> loader = FileSystemLoader('/path/to/templates')
    >>> loader = FileSystemLoader(['/path/to/templates', '/other/path'])

    Per default the template encoding is ``'utf-8'`` which can be changed
    by setting the `encoding` parameter to something else.
    """

    def __init__(self, searchpath, encoding='utf-8'):
        if isinstance(searchpath, string_types):
            searchpath = [searchpath]
        self.searchpath = list(searchpath)
        self.encoding = encoding

    def get_source(self, environment, template):
        pieces = split_template_path(template)
        for searchpath in self.searchpath:
            filename = path.join(searchpath, *pieces)
            f = open_if_exists(filename)
            if f is None:
                continue
            try:
                contents = f.read().decode(self.encoding)
            finally:
                f.close()

            mtime = path.getmtime(filename)
            def uptodate():
                try:
                    return path.getmtime(filename) == mtime
                except OSError:
                    return False
            return contents, filename, uptodate
        raise TemplateNotFound(template)

    def list_templates(self):
        found = set()
        for searchpath in self.searchpath:
            for dirpath, dirnames, filenames in filter_files(searchpath):
                for filename in filenames:
                    template = os.path.join(dirpath, filename) \
                        [len(searchpath):].strip(os.path.sep) \
                                          .replace(os.path.sep, '/')
                    if template[:2] == './':
                        template = template[2:]
                    if template not in found:
                        found.add(template)
        return sorted(found)


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
        command.__call__(args)
        sys.exit()

    else:
        show_error(colored.red('Error! Unknown command `{0}`.\n'
                               .format(args.get(0))))
        display_info()
        sys.exit(1)


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


def tarbell_generate(args):
    """Generate static files."""

    with ensure_settings(args) as settings, ensure_site(args) as site:
        output_root = list_get(args, 0, False)
        if not output_root:
            tempdir = tempfile.mkdtemp(prefix="{0}-".format(site.project.__name__))
            os.makedirs(os.path.join(tempdir, site.project.__name__))
            output_root = os.path.join(tempdir, site.project.__name__)
        else:
            tempdir = output_root
            output_root = os.path.join(tempdir, site.project.__name__)

        if args.contains('--context'):
            site.project.CONTEXT_SOURCE_FILE = args.value_after('--context')

        site.generate_static_site(output_root)
        puts("\nCreated site in {0}".format(output_root))
        return tempdir


def tarbell_list(args):
    """List tarbell projects."""
    with ensure_settings(args) as settings:
        print "list..."
        #cmd_branches(path)


def tarbell_publish(args):
    """Publish a site by calling s3cmd"""
    with ensure_settings(args) as settings, ensure_site(args) as site:
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


def tarbell_newproject(args):
    """Create new Tarbell project."""
    with ensure_settings(args) as settings:
        # Project settings
        name = args.get(0)
        while not name:
            name = raw_input("No project name specified. Please enter a project name: ")

        default_projects_path = settings.config.get("projects_path")
        projects_path = None

        if default_projects_path:
            projects_path = raw_input("Where would you like to create this project? [{0}] ".format(default_projects_path))
            if not projects_path:
                projects_path = default_projects_path
        else:
            while not projects_path:
                projects_path = raw_input("Where would you like to create this project? (e.g. ~/mytarbellsites/) ")

        path = os.path.join(projects_path, name)

        # Get template
        puts("\nPick a template")
        template = None
        while not template:
            puts("\n")
            for idx, option in enumerate(settings.config.get("project_templates"), start=1):
                puts("  {0:5} {1:36} {2}".format(colored.yellow("[{0}]".format(idx)),
                                               colored.green(option.get("name")),
                                               colored.yellow(option.get("url"))
                                              ))
            index = raw_input("\nWhich template would you like to use? ")
            try:
                index = int(index) - 1
                template = settings.config["project_templates"][index]
            except:
                pass

        tempdir = tempfile.mkdtemp(prefix="{0}-".format(name))
        puts("\nCloning {0} to {1}".format(template.get("url"), tempdir))
        Repo.clone_from(template.get("url"), tempdir)

        # Create spreadsheet/context vars
        # Copy project files

        if settings.client_secrets:
            puts("\nClient secrets available, creating spreadsheet...")
            key = _create_spreadsheet(name, tempdir, settings)
        print key
        #context = site._get_context_from_gdoc(key)
        #context['spreadsheet_key'] = key
        #_copy_project_files(project, path, context)

        # Delete tempdir
        try:
            shutil.rmtree(tempdir)  # delete directory
            puts("\nDeleted {0}".format(tempdir))
        except OSError as exc:
            if exc.errno != 2:  # code 2 - no such file or directory
                raise  # re-raise exception
        except UnboundLocalError:
            pass




def _copy_project_files(project, path, context):
    proj_dir = os.path.join(path, project)
    try:
        os.mkdir(proj_dir)
    except OSError, e:
        if e.errno == 17:
            print ("ABORTING: Directory %s "
                   "already exists.") % proj_dir
        else:
            print "ABORTING: OSError %s" % e
        return

    # Get and walk project template
    loader = jinja2.FileSystemLoader(os.path.join(path, '_project_template'))
    env = jinja2.Environment(loader=loader)

    for root, dirs, files in os.walk(os.path.join(path, '_project_template')):
        for filename in files:
            # Strip out full filesystem paths
            dirname = root.replace(path, "")\
                          .replace("_project_template", "")

            relpath = "{0}/{1}".format(dirname, filename)
            if relpath.startswith("/"):
                relpath = relpath[1:]

            filepath = os.path.join(root, filename)
            output_path = filepath.replace("_project_template", project)
            output_dir = os.path.dirname(output_path)

            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            mimetype, encoding = mimetypes.guess_type(filepath)

            puts("Writing {0}".format(colored.yellow(output_path)))
            if mimetype and mimetype.startswith("text/"):
                content = env.get_template(relpath).render(context)
                codecs.open(output_path, "w", encoding="utf-8").write(content)
            else:
                shutil.copy(filepath, output_path)


def _create_spreadsheet(project, path, settings):
    puts("\nGenerating Google spreadsheet")

    email_message = (
        "What Google account should have access to this "
        "this spreadsheet? Use a full email address, such as "
        "your.name@gmail.com or the Google account equivalent. ")

    if settings.config.get("google_account"):
        email = raw_input("{0}(Default: {1}) ".format(email_message,
                                             settings.config.get("google_account")
                                            ))
        if not email:
            email = settings.config.get("google_account")
    else:
        email = None
        while not email:
            email = raw_input(email_message)

    media_body = _MediaFileUpload(os.path.join(path,
                                  'data.xlsx'),
                                  mimetype='application/vnd.ms-excel')

    service = get_drive_api(settings.path)
    body = {
        'title': '%s [Tarbell project]' % project,
        'description': '%s [Tarbell project]' % project,
        'mimeType': 'application/vnd.ms-excel',
    }
    try:
        newfile = service.files()\
            .insert(body=body, media_body=media_body, convert=True).execute()
        _add_user_to_file(newfile['id'], service, user_email=email)
        puts(("Success! View the file at "
              "https://docs.google.com/spreadsheet/ccc?key={0}"
              .format(newfile['id'])))
        return newfile['id']
    except errors.HttpError, error:
        show_error('An error occurred: {0}'.format(error))
        sys.exit(1)


def _add_user_to_file(file_id, service, user_email,
                      perm_type='user', role='reader'):
    """
    Grants the given set of permissions for a given file_id. service is an
    already-credentialed Google Drive service instance.
    """
    new_permission = {
        'value': user_email,
        'type': perm_type,
        'role': role
    }
    try:
        service.permissions()\
            .insert(fileId=file_id, body=new_permission)\
            .execute()
    except errors.HttpError, error:
        print 'An error occurred: %s' % error


def tarbell_serve(args):
    """Serve the current Tarbell project."""
    with ensure_settings(args) as settings, ensure_site(args) as site:
        address = list_get(args, 0, "").split(":")
        ip = list_get(address, 0, '127.0.0.1')
        port = list_get(address, 1, 5000)
        site.app.run(ip, port=int(port))


def tarbell_switch(args):
    """Switch to a project"""
    with ensure_settings(args) as settings:
        #cmd_switch(args)               # legit switch
        tarbell_serve(args[1:], path)  # serve 'em up!


def tarbell_unpublish(args):
    with ensure_settings(args) as settings, ensure_site(args) as site:
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


# Note that the tarbell_configure function is imported from contextmanagers.py
def_cmd(
    name='configure',
    fn=tarbell_configure,
    usage='configure',
    help='Configure Tarbell.')


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
