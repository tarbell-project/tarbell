# -*- coding: utf-8 -*-

"""
tarbell.cli
~~~~~~~~~

This module provides the CLI interface to tarbell.
"""

import codecs
import glob
import gnureadline
import imp
import jinja2
import os
import pkg_resources
import sh
import shutil
import socket
import sys
import tempfile

from apiclient import errors
from apiclient.http import MediaFileUpload as _MediaFileUpload
from clint import arguments
from clint.textui import colored

from tarbell import __VERSION__ as VERSION

# Handle relative imports from binary, see https://github.com/newsapps/flask-tarbell/issues/87
if __name__ == "__main__" and __package__ is None:
    __package__ = "tarbell.cli"

from .app import pprint_lines, process_xlsx, copy_global_values
from .oauth import get_drive_api
from .contextmanagers import ensure_settings, ensure_project
from .configure import tarbell_configure
from .s3 import S3Url, S3Sync
from .settings import Settings
from .utils import list_get, split_sentences, show_error
from .utils import puts, is_werkzeug_process

# Set args
args = arguments.Args()


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
        command.__call__(command, args)
        sys.exit()

    else:
        show_error(colored.red('Error! Unknown command `{0}`.\n'
                               .format(args.get(0))))
        display_info(args)
        sys.exit(1)


def display_info(args):
    """Displays Tarbell info."""
    puts('\nTarbell: Simple web publishing\n')

    puts('Usage: {0}\n'.format(colored.cyan('tarbell <command>')))
    puts('Commands:\n')
    for command in Command.all_commands():
        usage = command.usage or command.name
        help = command.help or ''
        puts('{0} {1}'.format(
            colored.yellow('{0: <37}'.format(usage)),
            split_sentences(help, 37)
        ))
    puts("")

    settings = Settings()
    if settings.file_missing:
        puts('---\n{0}: {1}'.format(
            colored.red("Warning"),
            "No Tarbell configuration found. Run:"
        ))
        puts('\n{0}'.format(
            colored.green("tarbell configure")
        ))
        puts('\n{0}\n---'.format(
            "to configure Tarbell."
        ))

def display_version():
    """Displays Tarbell version/release."""
    puts('You are using Tarbell v{0}'.format(
        colored.green(VERSION)
    ))


def tarbell_generate(command, args, skip_args=False, extra_context=None, quiet=False):
    """Generate static files."""

    output_root = None
    with ensure_settings(command, args) as settings, ensure_project(command, args) as site:
        if not skip_args:
            output_root = list_get(args, 0, False)
            is_folder = os.path.exists(output_root)
        if quiet:
            site.quiet = True
        if not output_root:
            output_root = tempfile.mkdtemp(prefix="{0}-".format(site.project.__name__))
            is_folder = False

        if args.contains('--context'):
            site.project.CONTEXT_SOURCE_FILE = args.value_after('--context')

        if args.contains('--overwrite'):
            is_folder = False

        #check to see if the folder we're trying to create already exists
        if is_folder:
            output_file = raw_input(("\nA folder named {0} already exists! Do you want to delete it? (selecting 'N' will quit) [y/N] ").format(
                output_root
            ))
            if output_file and output_file.lower() == "y":
                puts(("\nDeleting {0}...\n").format(
                    colored.cyan(output_root)
                ))
                _delete_dir(output_root)
            else:
                puts("\nNot overwriting. See ya!")
                sys.exit()

        site.generate_static_site(output_root, extra_context)
        if not quiet:
            puts("\nCreated site in {0}".format(colored.cyan(output_root)))

        site.call_hook("generate", site, output_root, quiet)
        return output_root


def tarbell_install(command, args):
    """Install a project."""
    with ensure_settings(command, args) as settings:
        project_url = args.get(0)
        puts("\n- Getting project information for {0}".format(project_url))
        project_name = project_url.split("/").pop()
        message = None
        error = None

        # Create a tempdir and clone
        tempdir = tempfile.mkdtemp()
        try:
            testgit = sh.git.bake(_cwd=tempdir, _tty_out=False)
            puts(testgit.clone(project_url, '.', *['--depth=1', '--bare']))
            config = testgit.show("HEAD:tarbell_config.py")
            puts("\n- Found tarbell_config.py")
            path = _get_path(_clean_suffix(project_name, ".git"), settings)
            _mkdir(path)
            git = sh.git.bake(_cwd=path)
            puts(git.clone(project_url, '.'))
            puts(git.submodule.update(*['--init', '--recursive']))
            _install_requirements(path)

            # Get site, run hook
            with ensure_project(command, args, path) as site:
                site.call_hook("install", site, git)

            message = "\n- Done installing project in {0}".format(colored.yellow(path))

        except sh.ErrorReturnCode_128:
            error = "Not a Tarbell project!"
        finally:
            _delete_dir(tempdir)
            if message:
                puts(message)
            if error:
                show_error(error)

def tarbell_install_template(command, args):
    """Install a project template."""
    with ensure_settings(command, args) as settings:
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
        tempdir = tempfile.mkdtemp()
        git = sh.git.bake(_cwd=tempdir)
        puts(git.clone(template_url, '.'))
        puts(git.fetch())
        puts(git.checkout(VERSION))

        _install_requirements(tempdir)

        filename, pathname, description = imp.find_module('blueprint', [tempdir])
        blueprint = imp.load_module('blueprint', filename, pathname, description)
        puts("\n- Found _blueprint/blueprint.py")
        try:
            name = blueprint.NAME
            puts("\n- Name specified in blueprint.py: {0}".format(colored.yellow(name)))
        except AttributeError:
            name = template_url.split("/")[-1]
            puts("\n- No name specified in blueprint.py, using '{0}'".format(colored.yellow(name)))

        settings.config["project_templates"].append({"name": name, "url": template_url})
        settings.save()

        _delete_dir(tempdir)

        puts("\n+ Added new project template: {0}".format(colored.yellow(name)))


def tarbell_list(command, args):
    """List tarbell projects."""
    with ensure_settings(command, args) as settings:
        projects_path = settings.config.get("projects_path")
        if not projects_path:
            show_error("{0} does not exist".format(projects_path))
            sys.exit()

        puts("Listing projects in {0}\n".format(
            colored.yellow(projects_path)
        ))

        longest_title = 0
        projects = []
        for directory in os.listdir(projects_path):
            project_path = os.path.join(projects_path, directory)
            try:
                filename, pathname, description = imp.find_module('tarbell_config', [project_path])
                config = imp.load_module(directory, filename, pathname, description)
                title = config.DEFAULT_CONTEXT.get("title", directory)
                projects.append((directory, title))
                if len(title) > longest_title:
                    longest_title = len(title)
            except ImportError:
                pass

        if len(projects):
            fmt = "{0: <"+str(longest_title+1)+"} {1}"
            puts(fmt.format(
                'title',
                'project name'
            ))
            for projectname, title in projects:
                puts(colored.yellow(fmt.format(
                    title,
                    colored.cyan(projectname)
                )))

            puts("\nUse {0} to switch to a project".format(
                colored.green("tarbell switch <project name>")
                ))
        else:
            puts("No projects found")

def tarbell_list_templates(command, args):
    with ensure_settings(command, args) as settings:
        puts("\nAvailable project templates\n")
        _list_templates(settings)
        puts("")


def tarbell_publish(command, args):
    """Publish a site by calling s3cmd"""
    with ensure_settings(command, args) as settings, ensure_project(command, args) as site:
        bucket_name = list_get(args, 0, "staging")

        try:
            bucket_url = S3Url(site.project.S3_BUCKETS[bucket_name])
        except KeyError:
            show_error(
                "\nThere's no bucket configuration called '{0}' in "
                "tarbell_config.py.".format(colored.yellow(bucket_name)))
            sys.exit(1)

        extra_context = {
            "ROOT_URL": bucket_url,
            "S3_BUCKET": bucket_url.root,
            "BUCKET_NAME": bucket_name,
        }

        tempdir = "{0}/".format(tarbell_generate(command,
            args, extra_context=extra_context, skip_args=True, quiet=True))
        try:
            title = site.project.DEFAULT_CONTEXT.get("title", "")
            puts("\nDeploying {0} to {1} ({2})\n".format(
                colored.yellow(title),
                colored.red(bucket_name),
                colored.green(bucket_url)
            ))

            # Get creds
            if settings.config:
                # If settings has a config section, use it
                kwargs = settings.config['s3_credentials'].get(bucket_url.root)
                if not kwargs:
                    kwargs = {
                        'access_key_id': settings.config['default_s3_access_key_id'],
                        'secret_access_key': settings.config['default_s3_secret_access_key'],
                    }
                    puts("Using default bucket credentials")
                else:
                    puts("Using custom bucket configuration for {0}".format(bucket_url.root))
            else:
                # If no configuration exists, read from environment variables if possible
                puts("Attemping to use AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
                kwargs = {
                    'access_key_id': os.environ["AWS_ACCESS_KEY_ID"],
                    'secret_access_key': os.environ["AWS_SECRET_ACCESS_KEY"],
                }


            s3 = S3Sync(tempdir, bucket_url, **kwargs)
            s3.deploy_to_s3()
            site.call_hook("publish", site, s3)

            puts("\nIf you have website hosting enabled, you can see your project at:")
            puts(colored.green("http://{0}\n".format(bucket_url)))
        except KeyboardInterrupt:
            show_error("ctrl-c pressed, bailing out!")
        finally:
            _delete_dir(tempdir)


def _delete_dir(dir):
    """Delete tempdir"""
    try:
        shutil.rmtree(dir)  # delete directory
    except OSError as exc:
        if exc.errno != 2:  # code 2 - no such file or directory
            raise  # re-raise exception
    except UnboundLocalError:
        pass


def tarbell_newproject(command, args):
    """Create new Tarbell project."""
    with ensure_settings(command, args) as settings:
        # Set it up and make the directory
        name = _get_project_name(args)
        puts("Creating {0}".format(colored.cyan(name)))
        path = _get_path(name, settings)
        _mkdir(path)

        try:
            _newproject(command, path, name, settings)
        except KeyboardInterrupt:
            _delete_dir(path)
            show_error("ctrl-c pressed, not creating new project.")
        except:
            _delete_dir(path)
            show_error("Unexpected error: {0}".format(sys.exc_info()[0]))
            raise


def _newproject(command, path, name, settings):
    """Actual heavy lifting for project creation."""
    key = None
    title = _get_project_title()
    template = _get_template(settings)

    # Init repo
    git = sh.git.bake(_cwd=path)
    puts(git.init())

    if template.get("url"):
        # Create submodule
        puts(git.submodule.add(template['url'], '_blueprint'))
        puts(git.submodule.update(*['--init']))

        # Get submodule branches, switch to current version
        submodule = sh.git.bake(_cwd=os.path.join(path, '_blueprint'))
        puts(submodule.fetch())
        puts(submodule.checkout(VERSION))

        # Create spreadsheet
        key = _create_spreadsheet(name, title, path, settings)

        # Copy html files
        puts(colored.green("\nCopying html files..."))
        files = glob.iglob(os.path.join(path, "_blueprint", "*.html"))
        for file in files:
            if os.path.isfile(file):
                dir, filename = os.path.split(file)
                if not filename.startswith("_") and not filename.startswith("."):
                    puts("Copying {0} to {1}".format(filename, path))
                    shutil.copy2(file, path)
        ignore = os.path.join(path, "_blueprint", ".gitignore")
        if os.path.isfile(ignore):
            shutil.copy2(ignore, path)
    else:
        empty_index_path = os.path.join(path, "index.html")
        open(empty_index_path, "w")

    # Create config file
    _copy_config_template(name, title, template, path, key, settings)

    # Commit
    puts(colored.green("\nInitial commit"))
    puts(git.add('.'))
    puts(git.commit(m='Created {0} from {1}'.format(name, template['name'])))

    _install_requirements(path)

    # Get site, run hook
    with ensure_project(command, args, path) as site:
        site.call_hook("newproject", site, git)

    # Messages
    puts("\nAll done! To preview your new project, type:\n")
    puts("{0} {1}".format(colored.green("tarbell switch"), colored.green(name)))
    puts("\nor\n")
    puts("{0}".format(colored.green("cd %s" % path)))
    puts("{0}".format(colored.green("tarbell serve\n")))

    puts("\nYou got this!\n")


def _install_requirements(path):
    """Install requirements.txt"""
    locations = [os.path.join(path, "_blueprint"), os.path.join(path, "_base"), path] 
    success = True

    for location in locations:
        try:
            with open(os.path.join(location, "requirements.txt")):
                puts("\nRequirements file found at {0}".format(os.path.join(location, "requirements.txt")))
                install_reqs = raw_input("Install requirements now with pip install -r requirements.txt? [Y/n] ")
                if not install_reqs or install_reqs.lower() == 'y':
                    pip = sh.pip.bake(_cwd=location)
                    puts("\nInstalling requirements...")
                    puts(pip("install", "-r", "requirements.txt"))
                else:
                    success = False
                    puts("Not installing requirements. This may break everything! Vaya con dios.")
        except IOError:
            pass

    return success


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


def _clean_suffix(string, suffix):
    """If string endswith the suffix, remove it. Else leave it alone"""
    suffix_len = len(suffix)

    if len(string) < suffix_len:
        # the string param was shorter than the suffix
        raise ValueError("A suffix can not be bigger than string argument.")
    if string.endswith(suffix):
        # return from the beginning up to
        # but not including the first letter
        # in the suffix
        return string[0:-suffix_len]   
    else:
        # leave unharmed
        return string


def _get_path(name, settings, mkdir=True):
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

    return os.path.expanduser(path)


def _mkdir(path):
    """Make a directory or bail."""
    try:
        os.mkdir(path)
    except OSError, e:
        if e.errno == 17:
            show_error("ABORTING: Directory {0} already exists.".format(path))
        else:
            show_error("ABORTING: OSError {0}".format(e))
        sys.exit()


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
        puts("  {0:5} {1:36}".format(
            colored.yellow("[{0}]".format(idx)),
            colored.cyan(option.get("name"))
        ))
        if option.get("url"):
            puts("      {0}\n".format(option.get("url")))


def _create_spreadsheet(name, title, path, settings):
    """Create Google spreadsheet"""
    if not settings.client_secrets:
        return None

    create = raw_input("Would you like to create a Google spreadsheet? [Y/n] ")

    if create and not create.lower() == "y":
        return puts("Not creating spreadsheet.")

    email_message = (
        "What Google account(s) should have access to this "
        "this spreadsheet? (Use a full email address, such as "
        "your.name@gmail.com. Separate multiple addresses with commas.)")

    if settings.config.get("google_account"):
        emails = raw_input("\n{0}(Default: {1}) ".format(email_message,
                                             settings.config.get("google_account")
                                            ))
        if not emails:
            emails = settings.config.get("google_account")
    else:
        emails = None
        while not emails:
            emails = raw_input(email_message)

    try:
        media_body = _MediaFileUpload(os.path.join(path, '_blueprint/_spreadsheet.xlsx'),
                                      mimetype='application/vnd.ms-excel')
    except IOError:
        show_error("_blueprint/_spreadsheet.xlsx doesn't exist!")
        return None

    service = get_drive_api()
    body = {
        'title': '{0} (Tarbell)'.format(title),
        'description': '{0} ({1})'.format(title, name),
        'mimeType': 'application/vnd.ms-excel',
    }
    try:
        newfile = service.files()\
            .insert(body=body, media_body=media_body, convert=True).execute()
        for email in emails.split(","):
            _add_user_to_file(newfile['id'], service, user_email=email.strip())
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
                      perm_type='user', role='writer'):
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
        show_error('An error adding users to spreadsheet: {0}'.format(error))


def _copy_config_template(name, title, template, path, key, settings):
        """Get and render tarbell_config.py.template from blueprint"""
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
            spreadsheet_path = os.path.join(path, '_blueprint/', '_spreadsheet.xlsx')
            try:
                with open(spreadsheet_path, "rb") as f:
                    puts("Copying _blueprint/_spreadsheet.xlsx to tarbell_config.py's DEFAULT_CONTEXT") 
                    data = process_xlsx(f.read())
                    if 'values' in data:
                        data = copy_global_values(data)
                    context["default_context"].update(data)
            except IOError:
                pass

        s3_buckets = settings.config.get("s3_buckets")
        if s3_buckets:
            puts("")
            for bucket, bucket_conf in s3_buckets.items():
                puts("Configuring {0} bucket at {1}\n".format(
                    colored.green(bucket),
                    colored.yellow("{0}/{1}".format(bucket_conf['uri'], name))
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


def tarbell_serve(command, args):
    """Serve the current Tarbell project."""
    with ensure_project(command, args) as site:
        address = list_get(args, 0, "").split(":")
        ip = list_get(address, 0, '127.0.0.1')
        port = int(list_get(address, 1, '5000'))
        puts("\n * Running local server. Press {0} to stop the server".format(colored.red("ctrl-c")))
        puts(" * Edit this project's templates at {0}".format(colored.yellow(site.path)))
        try:
            if not is_werkzeug_process():
                site.call_hook("server_start", site)

            site.app.run(ip, port=port)

            if not is_werkzeug_process():
                site.call_hook("server_stop", site)

        except socket.error:
            show_error("Address {0} is already in use, please try another port or address."
                 .format(colored.yellow("{0}:{1}".format(ip, port))))


def tarbell_switch(command, args):
    """Switch to a project"""
    with ensure_settings(command, args) as settings:
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
            tarbell_serve(command, args)
        else:
            show_error("{0} isn't a tarbell project".format(project_path))


def tarbell_update(command, args):
    """Update the current tarbell project."""
    with ensure_settings(command, args) as settings, ensure_project(command, args) as site:
        puts("Updating to latest blueprint\n")

        git = sh.git.bake(_cwd=site.base.base_dir)
        git.fetch()
        puts(colored.yellow("Checking out {0}".format(VERSION)))
        puts(git.checkout(VERSION))
        puts(colored.yellow("Stashing local changes"))
        puts(git.stash())
        puts(colored.yellow("Pull latest changes"))
        puts(git.pull('origin', VERSION))



def tarbell_unpublish(command, args):
    with ensure_settings(command, args) as settings, ensure_project(command, args) as site:
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
    usage='configure <subcommand (optional)>',
    help="Configure Tarbell. Subcommand can be one of 'drive', 's3', 'path', or 'templates'.")


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
    help='Update blueprint in current project.')


def_cmd(
    name='unpublish',
    fn=tarbell_unpublish,
    usage='unpublish <target (default: staging)>',
    help='Remove the current project from <target>.')

