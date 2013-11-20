# -*- coding: utf-8 -*-

"""
tarbell.cli
~~~~~~~~~

This module provides the CLI interface to tarbell.
"""

import os
import glob
import sh
import sys
import imp
import jinja2
import codecs
import tempfile
import shutil
import pkg_resources

from subprocess import call
from clint import args
from clint.textui import colored, puts

from apiclient import errors
from apiclient.http import MediaFileUpload as _MediaFileUpload

from git import Repo

from .app import pprint_lines, process_xlsx, copy_global_values
from .oauth import get_drive_api
from .contextmanagers import ensure_settings, ensure_project
from .configure import tarbell_configure
from .utils import list_get, black, split_sentences, show_error, get_config_from_args
from tarbell import __VERSION__ as VERSION

__version__ = '0.9'


# --------
# Dispatch
# --------
def main():
    """Primary Tarbell command dispatch."""

    command = Command.lookup(args.get(0))

    if len(args) == 0 or args.contains(('-h', '--help', 'help')):
        display_info(args)
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
        display_info(args)
        sys.exit(1)


def display_info(args):
    """Displays Tarbell info."""
    puts('\n{0}\n'.format(
        black('Tarbell: Simple web publishing'),
    ))

    puts('Usage: {0}\n'.format(colored.cyan('tarbell <command>')))
    puts('Commands:\n')
    for command in Command.all_commands():
        usage = command.usage or command.name
        help = command.help or ''
        puts('{0:50} {1}'.format(
                colored.green(usage),
                split_sentences(help)))

    puts('\nOptions\n')
    puts('{0:50} {1}'.format(
        colored.green("--reset-creds"),
        'Reset Google Drive OAuth2 credentials'
    ))
    puts('{0:50} {1}'.format(
        colored.green("--settings <path>"),
        'Path to settings directory.'
    ))

    config = get_config_from_args(args)
    if not os.path.isdir(config):
        puts('\n---\n\n{0}: {1}'.format(
            colored.red("Warning"),
            "No Tarbell configuration found. Run:"
        ))
        puts('\n    {0}'.format(
            colored.green("tarbell configure")
        ))
        puts('\n{0}'.format(
            "to configure Tarbell."
        ))

    puts('\n{0}'.format(
        black(u'Crafted by the Chicago Tribune News Applications team\n')
    ))


def display_version():
    """Displays Legit version/release."""

    puts('{0} v{1}'.format(
        colored.yellow('Tarbell'),
        __version__
    ))


def tarbell_generate(args, skip_args=False, extra_context=None):
    """Generate static files."""

    output_root = None
    with ensure_settings(args) as settings, ensure_project(args) as site:
        if not skip_args:
            output_root = list_get(args, 0, False)
        if not output_root:
            output_root = tempfile.mkdtemp(prefix="{0}-".format(site.project.__name__))

        if args.contains('--context'):
            site.project.CONTEXT_SOURCE_FILE = args.value_after('--context')

        site.generate_static_site(output_root, extra_context)
        puts("\nCreated site in {0}".format(output_root))
        return output_root


def tarbell_install(args):
    """Install a project."""
    with ensure_settings(args) as settings:
        project_url = args.get(0)
        puts("\n- Getting project information for {0}".format(project_url)) 
        tempdir = tempfile.mkdtemp()
        Repo.clone_from(project_url, tempdir)
        filename, pathname, description = imp.find_module('tarbell', [tempdir])
        config = imp.load_module('tarbell', filename, pathname, description)
        puts("\n- Found config.py")
        path = _get_path(config.NAME, settings)
        repo = Repo.clone_from(project_url, path)
        try:
            puts("\n- Adding remote 'updated_project_template' using {0}".format(config.TEMPLATE_REPO_URL))
            repo.create_remote("update_project_template", config.TEMPLATE_REPO_URL)
        except AttributeError:
            pass
        _delete_dir(tempdir)
        puts("\n- Done installing project in {0}".format(path))


def tarbell_install_template(args):
    """Install a project template."""
    with ensure_settings(args) as settings:
        template_url = args.get(0)

        matches = [template for template in settings.config["project_templates"] if template["url"] == template_url]
        if matches:
            puts("\n{0} already exists. Nothing more to do.\n".format(
                colored.yellow(template_url)
            ))
            sys.exit()

        puts("\nInstalling {0}".format(colored.cyan(template_url))) 
        tempdir = tempfile.mkdtemp()
        puts("\n- Cloning repo to {0}".format(colored.green(tempdir))) 
        Repo.clone_from(template_url, tempdir)
        base_path = os.path.join(tempdir, "_base/")
        filename, pathname, description = imp.find_module('base', [base_path])
        base = imp.load_module('base', filename, pathname, description)
        puts("\n- Found _base/base.py")
        try:
            name = base.NAME
            puts("\n- Name specified in base.py: {0}".format(colored.yellow(name)))
        except AttributeError:
            name = template_url.split("/")[-1]
            puts("\n- No name specified in base.py, using '{0}'".format(colored.yellow(name)))

        settings.config["project_templates"].append({"name": name, "url": template_url})
        settings.save()

        _delete_dir(tempdir)

        puts("\n+ Added new project template: {0}".format(colored.yellow(name)))


def tarbell_list(args):
    """List tarbell projects."""
    with ensure_settings(args) as settings:
        projects_path = settings.config.get("projects_path")
        if not projects_path:
            show_error("{0} does not exist".format(projects_path))
            sys.exit()

        puts("\nListing projects in {0}\n".format(
            colored.yellow(projects_path)
        ))

        for dir in os.listdir(projects_path):
            project_path = os.path.join(projects_path, dir)
            try:
                filename, pathname, description = imp.find_module('tarbell', [project_path])
                config = imp.load_module(dir, filename, pathname, description)

                puts("{0:37} {1}".format(
                    colored.red(config.NAME),
                    colored.cyan(config.TITLE)
                ))

                puts("- {0:25} {1}".format("Project path:", colored.yellow(project_path))),
                repo = Repo(project_path)

                try:
                    origin = repo.remotes.origin.config_reader.get_value("url")
                    puts("- {0:25} {1}".format("Project repository:", origin))
                except AttributeError:
                    pass

                try:
                    update_project_template = repo.remotes.update_project_template.config_reader.get_value("url")
                    puts("- {0:25} {1}".format("Base update repository:", update_project_template))
                except AttributeError:
                    pass

                puts("")

            except ImportError:
                pass

        puts("Use {0} to switch to a project\n".format(
            colored.green("tarbell switch <projectname>")
            ))


def tarbell_list_templates(args):
    with ensure_settings(args) as settings:
        puts("\nAvailable project templates\n")
        _list_templates(settings)
        puts("")


def tarbell_publish(args):
    """Publish a site by calling s3cmd"""
    with ensure_settings(args) as settings, ensure_project(args) as site:
        bucket_name = list_get(args, 0, "staging")
        bucket_uri = site.project.S3_BUCKETS.get(bucket_name, False)

        root_url = bucket_uri[5:]
        extra_context = {
            "ROOT_URL": root_url,
        }

        tempdir = "{0}/".format(tarbell_generate(args, extra_context=extra_context, skip_args=True))
        try:
            if bucket_uri:
                puts("\nDeploying {0} to {1} ({2})".format(
                      colored.yellow(site.project.TITLE),
                      colored.red(bucket_name),
                      colored.green(bucket_uri)
                     ))
                command = ['s3cmd', 'sync', '--acl-public', '--verbose', tempdir, bucket_uri]
                puts("\nCalling {0}".format(colored.yellow(" ".join(command))))
                call(command)
            else:
                show_error(("\nThere's no bucket configuration called '{0}' "
                            "in tarbell_config.py.".format(colored.yellow(bucket_name))))
        except KeyboardInterrupt:
            show_error("ctrl-c pressed, bailing out!")
        finally:
            puts("\nIf you have website hosting enabled, you can see your project at http://{0}".format(root_url))
            puts("\n- Done publishing")
            _delete_dir(tempdir)


def _delete_dir(dir):
    """Delete tempdir"""
    try:
        shutil.rmtree(dir)  # delete directory
        puts("\nDeleted {0}!".format(dir))
    except OSError as exc:
        if exc.errno != 2:  # code 2 - no such file or directory
            raise  # re-raise exception
    except UnboundLocalError:
        pass


def tarbell_newproject(args):
    """Create new Tarbell project."""
    with ensure_settings(args) as settings:

        # Create directory or bail
        name = _get_project_name(args)
        puts("Creating {0}".format(colored.cyan(name)))
        path = _get_path(name, settings)
        title = _get_project_title()
        template = _get_template(settings)

        # Init repo
        git = sh.git.bake(_cwd=path)
        puts(git.init())

        # Create submodule
        puts(git.submodule.add(template['url'], '_base'))
        puts(git.submodule.update(*['--init']))

        # Get submodule branches, switch to current version
        submodule = sh.git.bake(_cwd=os.path.join(path, '_base'))
        puts(submodule.fetch())
        puts(submodule.checkout(VERSION))

        # Create spreadsheet
        key = _create_spreadsheet(name, title, path, settings)

        # Create config file
        _copy_config_template(name, title, template, path, key, settings)

        # Copy html files
        puts(colored.green("\nCopying html files..."))
        files = glob.iglob(os.path.join(path, "_base", "*.html"))
        for file in files:
            if os.path.isfile(file):
                dir, filename = os.path.split(file)
                if not filename.startswith("_") and not filename.startswith("."):
                    puts("Copying {0} to {1}".format(filename, path))
                    shutil.copy2(file, path)

        # Commit
        puts(colored.green("\nInitial commit"))
        puts(git.add('.'))
        puts(git.commit(m='Created {0} from {1}'.format(name, template['url'])))

        # Set up remote url
        remote_url = raw_input("\nWhat is the URL of your project repository? (e.g. git@github.com:myaccount/myproject.git, leave blank to skip) ")
        if remote_url:
            puts("\nCreating new remote 'origin' to track {0}.".format(colored.yellow(remote_url)))
            git.remote.add(*["origin", remote_url])
            puts("\n{0}: Don't forget! It's up to you to create this remote and push to it.".format(colored.cyan("Warning")))
        else:
            puts("\n- Not setting up remote repository. Use your own version control!")


        # Messages
        puts("\nAll done! To preview your new project, type:\n")
        puts("{0} {1}".format(colored.green("tarbell switch"), colored.green(name)))
        puts("\nor\n")
        puts("{0}".format(colored.green("cd %s" % path)))
        puts("{0}".format(colored.green("tarbell serve\n")))

        puts("\nYou got this!\n")


def _get_project_name(args):
        """Get project name"""
        name = args.get(0)
        puts("")
        while not name:
            name = raw_input("What is the project's short directory name? (e.g. my_project) ")
        return name


def _get_project_title():
        """Get project title"""
        title = None
        puts("")
        while not title:
            title = raw_input("What is the project's full title? (e.g. My awesome project) ")

        return title


def _get_path(name, settings):
    """Generate a project path."""
    default_projects_path = settings.config.get("projects_path")
    path = None

    if default_projects_path:
        path = raw_input("\nWhere would you like to create this project? [{0}/{1}] ".format(default_projects_path, name))
        if not path:
            path = os.path.join(default_projects_path, name)
    else:
        while not path:
            path = raw_input("\nWhere would you like to create this project? (e.g. ~/tarbell/) ")

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
    """Prompt user to pick template from a list."""
    puts("\nPick a template\n")
    template = None
    while not template:
        _list_templates(settings)
        index = raw_input("\nWhich template would you like to use? [1] ")
        if not index:
            index = "1"
        try:
            index = int(index) - 1
            return settings.config["project_templates"][index]
        except:
            puts("\"{0}\" isn't a valid option!".format(colored.red("{0}".format(index))))
            pass


def _list_templates(settings):
    """List templates from settings."""
    for idx, option in enumerate(settings.config.get("project_templates"), start=1):
        puts("  {0:5} {1:36}\n      {2}\n".format(
            colored.yellow("[{0}]".format(idx)),
            colored.cyan(option.get("name")),
            option.get("url")
        ))


def _create_spreadsheet(name, title, path, settings):
    """Create Google spreadsheet"""
    if not settings.client_secrets:
        return None

    create = raw_input("{0} found. Would you like to create a Google spreadsheet? [Y/n] ".format(
        colored.cyan("client_secrets")
    ))
    if create and not create.lower() == "y":
        return puts("Not creating spreadsheet...")

    email_message = (
        "What Google account should have access to this "
        "this spreadsheet? (Use a full email address, such as "
        "your.name@gmail.com or the Google account equivalent.) ") 

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
        media_body = _MediaFileUpload(os.path.join(path, '_base/_spreadsheet.xlsx'),
                                      mimetype='application/vnd.ms-excel')
    except IOError:
        show_error("_base/_spreadsheet.xlsx doesn't exist!")
        return None

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
        puts("\n{0}! View the spreadsheet at {1}".format(
            colored.green("Success"),
            colored.yellow("https://docs.google.com/spreadsheet/ccc?key={0}"
                           .format(newfile['id']))
            ))
        return newfile['id']
    except errors.HttpError, error:
        show_error('An error occurred creating spreadsheet: {0}'.format(error))
        return None


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


def _copy_config_template(name, title, template, path, key, settings):
        """Get and render tarbell_config.py.template from base"""
        puts("\nCopying configuration file")
        context = settings.config
        context.update({
            "default_context": {
                "name": name,
                "title": title,
            },
            "name": name,
            "title": title,
            "template_repo_url": template.get('url'),
            "key": key,
        })

        # @TODO refactor this a bit
        if not key:
            spreadsheet_path = os.path.join(path, '_base/', '_spreadsheet.xlsx')
            with open(spreadsheet_path, "rb") as f:
                try:
                    puts("Copying _base/_spreadsheet.xlsx to tarbell_config.py's DEFAULT_CONTEXT") 
                    data = process_xlsx(f.read())
                    if 'values' in data:
                        data = copy_global_values(data)
                    context["default_context"].update(data)
                except IOError:
                    show_error("No spreadsheet available")

        s3_buckets = settings.config.get("s3_buckets")
        if s3_buckets:
            puts("")
            for bucket, url in s3_buckets.items():
                puts("Configuring {0} bucket at {1}\n".format(
                        colored.green(bucket),
                        colored.yellow("{0}/{1}".format(url, name))
                    ))

        puts("\n- Creating {0} project configuration file".format(
            colored.cyan("tarbell_config.py")
        ))
        template_dir = os.path.dirname(pkg_resources.resource_filename("tarbell", "templates/tarbell_config.py.template"))
        loader = jinja2.FileSystemLoader(template_dir)
        env = jinja2.Environment(loader=loader)
        env.filters["pprint_lines"] = pprint_lines  # For dumping context
        content = env.get_template('tarbell_config.py.template').render(context)
        codecs.open(os.path.join(path, "tarbell_config.py"), "w", encoding="utf-8").write(content)
        puts("\n- Done copying configuration file")


def tarbell_serve(args):
    """Serve the current Tarbell project."""
    with ensure_project(args) as site:
        address = list_get(args, 0, "").split(":")
        ip = list_get(address, 0, '127.0.0.1')
        port = list_get(address, 1, '5000')
        puts("Press {0} to stop the server".format(colored.red("ctrl-c")))
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts/runserver.py')
        command = ['python', script, site.path, ip, port]
        try:
            call(command)
        except KeyboardInterrupt:
            puts(colored.red("Quitting with ctrl-c..."))


def tarbell_switch(args):
    """Switch to a project"""
    with ensure_settings(args) as settings:
        projects_path = settings.config.get("projects_path")
        if not projects_path:
            show_error("{0} does not exist".format(projects_path))
            sys.exit()
        project = args.get(0)
        args.remove(project)
        project_path = os.path.join(projects_path, project)
        if os.path.isdir(project_path):
            os.chdir(project_path)
            puts("\nSwitching to {0}".format(colored.red(project)))
            puts("Edit this project's templates at {0}".format(colored.yellow(project_path)))
            puts("Running preview server...")
            tarbell_serve(args)
        else:
            show_error("{0} isn't a tarbell project".format(project_path))


def tarbell_update(args):
    """Update the current tarbell project."""
    with ensure_settings(args) as settings, ensure_project(args) as site:
        repo = Repo(site.path)
        repo.remotes.update_project_template.fetch()
        repo.remotes.update_project_template.pull("master")
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
    help='Configure Tarbell')


def_cmd(
    name='generate',
    fn=tarbell_generate,
    usage='generate <output dir (optional)>',
    help=('Generate static files for the current project. If no output '
          'directory is specified, create a temporary directory'))


def_cmd(
    name='install',
    fn=tarbell_install,
    usage='install <url to project repository>',
    help='Install a pre-existing project')


def_cmd(
    name='install-template',
    fn=tarbell_install_template,
    usage='install-template <url to template>',
    help='Install a project template')


def_cmd(
    name='list',
    fn=tarbell_list,
    usage='list',
    help='List all projects.')

def_cmd(
    name='list-templates',
    fn=tarbell_list_templates,
    usage='list-templates',
    help='List installed project templates')

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
          '`192.168.56.1:8080`'))


def_cmd(
    name='switch',
    fn=tarbell_switch,
    usage='switch <project> <address (optional)>',
    help=('Switch to the project named <project> and start a preview server. '
          'Supply an optional address for the preview server such as '
          '`192.168.56.1:8080`'))


def_cmd(
    name='update',
    fn=tarbell_update,
    usage='update',
    help='Update base template in current project.')


def_cmd(
    name='unpublish',
    fn=tarbell_unpublish,
    usage='unpublish <target (default: staging)>',
    help='Remove the current project from <target>.')
