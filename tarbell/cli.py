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
from .contextmanagers import ensure_settings, ensure_project
from .configure import tarbell_configure
from .utils import list_get, black, split_sentences, show_error

__version__ = '0.9'


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


def tarbell_generate(args, skip_args=False):
    """Generate static files."""

    output_root = None
    with ensure_settings(args) as settings, ensure_project(args) as site:
        if not skip_args:
            output_root = list_get(args, 0, False)
        if not output_root:
            output_root = tempfile.mkdtemp(prefix="{0}-".format(site.project.__name__))

        if args.contains('--context'):
            site.project.CONTEXT_SOURCE_FILE = args.value_after('--context')

        site.generate_static_site(output_root)
        puts("\nCreated site in {0}".format(output_root))
        return output_root


def tarbell_list(args):
    """List tarbell projects."""
    with ensure_settings(args) as settings:
        print "list..."
        #cmd_branches(path)


def tarbell_publish(args):
    """Publish a site by calling s3cmd"""
    with ensure_settings(args) as settings, ensure_project(args) as site:
        bucket_name = list_get(args, 0, "staging")
        bucket_uri = site.project.S3_BUCKETS.get(bucket_name, False)

        try:
            if bucket_uri:
                tempdir = "%s/" % tarbell_generate(args, skip_args=True)
                puts("\nDeploying {0} to {1} ({2})".format(
                      colored.yellow(site.project.TITLE),
                      colored.red(bucket_name),
                      colored.green(bucket_uri)
                     ))
                command = ['s3cmd', 'sync', '--acl-public', '--delete-removed',
                           '--verbose', tempdir, bucket_uri]
                puts("\nCalling {0}".format(colored.yellow(" ".join(command))))
                call(command)
            else:
                show_error(("\nThere's no bucket configuration called '{0}' "
                            "in tarbell.py.".format(colored.yellow(bucket_name))))
        except KeyboardInterrupt:
            show_error("ctrl-c pressed, bailing out!")
        finally:
            # Delete tempdir
            try:
                shutil.rmtree(tempdir)  # delete directory
                puts("\nDeleted {0}!".format(tempdir))
            except OSError as exc:
                if exc.errno != 2:  # code 2 - no such file or directory
                    raise  # re-raise exception
            except UnboundLocalError:
                pass


def tarbell_newproject(args):
    """Create new Tarbell project."""
    with ensure_settings(args) as settings:
        name = _get_project_name(args)
        path = _get_path(name, settings)
        title = _get_project_title()
        template = _get_template(settings)
        repo = _clone_repo(template, path)

        _create_spreadsheet(name, title, path, settings)
        _copy_config_template(name, title, template, path, settings)
        _configure_remotes(name, template, repo)

        puts("\nAll done! To preview your new project, type:\n")
        puts("    {0}".format(colored.green("cd %s" % path)))
        puts("    {0}".format(colored.green("tarbell serve\n")))


def _get_project_name(args):
        """Get project name"""
        name = args.get(0)
        while not name:
            name = raw_input("No project name specified. Please enter a project name: ")
        return name


def _get_project_title():
        """Get project title"""
        title = None
        while not title:
            title = raw_input("Please enter a long name for this project: ")

        return title


def _get_path(name, settings):
    """Generate a project path."""
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
    try:
        os.mkdir(path)
    except OSError, e:
        if e.errno == 17:
            show_error("ABORTING: Directory {0} already exists.".format(path))
        else:
            show_error("ABORTING: OSError {0}".format(e))
        sys.exit()

    return path


def _get_template(settings):
    puts("\nPick a template\n")
    template = None
    while not template:
        for idx, option in enumerate(settings.config.get("project_templates"), start=1):
            puts("  {0:5} {1:36} {2}".format(colored.yellow("[{0}]".format(idx)),
                                           colored.green(option.get("name")),
                                           colored.yellow(option.get("url"))
                                          ))
        index = raw_input("\nWhich template would you like to use? [1] ")
        if not template:
            index = "1"
        try:
            index = int(index) - 1
            return settings.config["project_templates"][index]
        except:
            puts("\"{0}\" isn't a valid option!".format(colored.red("{0}".format(index))))
            pass


def _clone_repo(template, path):
    """Clone a template"""
    template_url = template.get("url")
    puts("\nCloning {0} to {1}".format(template_url, path))
    return Repo.clone_from(template_url, path)


def _create_spreadsheet(name, title, path, settings):
    """Create Google spreadsheet"""
    if settings.client_secrets:
        create = raw_input("\nclient_secrets.json found. Would you like to create a Google spreadsheet? [Y/n] ")
        if create and not create.lower() == "y":
            return puts("Not creating spreadsheet...")

    email_message = (
        "What Google account should have access to this "
        "this spreadsheet? Use a full email address, such as "
        "your.name@gmail.com or the Google account equivalent. ")

    if settings.config.get("google_account"):
        email = raw_input("\n{0}(Default: {1}) ".format(email_message,
                                             settings.config.get("google_account")
                                            ))
        if not email:
            email = settings.config.get("google_account")
    else:
        email = None
        while not email:
            email = raw_input(email_message)

    try:
        media_body = _MediaFileUpload(os.path.join(path, '_base/_config/'
                                      'spreadsheet_values.xlsx'),
                                      mimetype='application/vnd.ms-excel')
    except IOError:
        show_error("_base/_config/spreadsheet_values.xlsx doesn't exist!")
        return

    service = get_drive_api(settings.path)
    body = {
        'title': '{0} (Tarbell)'.format(title),
        'description': '{0} ({1})'.format(title, name),
        'mimeType': 'application/vnd.ms-excel',
    }
    try:
        newfile = service.files()\
            .insert(body=body, media_body=media_body, convert=True).execute()
        _add_user_to_file(newfile['id'], service, user_email=email)
        puts("Success! View the spreadsheet at {0}".format(
            colored.yellow("https://docs.google.com/spreadsheet/ccc?key={0}"
                           .format(newfile['id'])
                          )
            ))
        return newfile['id']
    except errors.HttpError, error:
        show_error('An error occurred creating spreadsheet: {0}'.format(error))


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


def _copy_config_template(name, title, template, path, settings):
        """Get and render tarbell.py.template from base"""

        puts("\nCreating tarbell.py project configuration file")
        context = settings.config
        context.update({
            "name": name,
            "title": title,
            "template_repo_url": template.get('url')
        })
        s3_buckets = settings.config.get("s3_buckets")
        if s3_buckets:
            print "\n"
            for bucket, url in s3_buckets.items():
                puts("Configuring {0} bucket at {1}".format(
                        colored.green(bucket),
                        colored.yellow("{0}/{1}".format(url, name))
                    ))

        config_template = os.path.join(path, "_base/_config/tarbell.py.template")
        if os.path.exists(config_template):
            puts("\nCopying configuration file...")
            loader = jinja2.FileSystemLoader(os.path.join(path, '_base/_config'))
            env = jinja2.Environment(loader=loader)
            content = env.get_template('tarbell.py.template').render(context)
            codecs.open(os.path.join(path, "tarbell.py"), "w", encoding="utf-8").write(content)


def _configure_remotes(name, template, repo):
    """Shuffle remotes"""
    puts("\nSetting up project repository...")
    puts("\nRenaming {0} to {1}".format(colored.yellow("master"), colored.yellow("update_project_template")))
    repo.remotes.origin.rename("update_project_template")
    root_path = "/".join(template.get("url").split("/")[0:-1])
    remote_url_suggestion = "{0}/{1}".format(root_path, name)
    remote_url = raw_input("What is the URL of your project repository? [{0}] ".format(remote_url_suggestion))
    if not remote_url:
        remote_url = remote_url_suggestion
    puts("\nCreating new remote 'origin' to track {0}.".format(colored.yellow(remote_url)))
    repo.create_remote("origin", remote_url)
    puts("{0}: It's up to you to create this repository!".format(colored.red("Don't forget")))


def tarbell_serve(args):
    """Serve the current Tarbell project."""
    with ensure_settings(args) as settings, ensure_project(args) as site:
        address = list_get(args, 0, "").split(":")
        ip = list_get(address, 0, '127.0.0.1')
        port = list_get(address, 1, 5000)
        puts("Press {0} to stop the server".format(colored.red("ctrl-c")))
        site.app.run(ip, port=int(port))


def tarbell_switch(args):
    """Switch to a project"""
    show_error("Not implemented!")


def tarbell_updateproject(args):
    """Update the current tarbell project."""
    with ensure_settings(args) as settings, ensure_project(args) as site:
        repo = Repo(site.path)
        repo.remotes.update_project_template.fetch()
        repo.remotes.update_project_template.pull()
        # @TODO make this chatty

def tarbell_unpublish(args):
    with ensure_settings(args) as settings, ensure_project(args) as site:
        """Delete a project."""
        show_error("Not implemented!")


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
    name='updateproject',
    fn=tarbell_updateproject,
    usage='updateproject',
    help='Update base template in current project.')


def_cmd(
    name='unpublish',
    fn=tarbell_unpublish,
    usage='unpublish <target (default: staging)>',
    help='Remove the current project from <target>.')
