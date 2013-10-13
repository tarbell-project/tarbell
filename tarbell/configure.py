# -*- coding: utf-8 -*-

"""
tarbell.configure
~~~~~~~~~~~~~~~~~

This module provides the Tarbell configure command.
"""

import os
import sys
import yaml
import shutil

from subprocess import call
from datetime import datetime
from clint.textui import colored, puts

from .app import TarbellSite
from .settings import Settings
from .oauth import get_drive_api
from .utils import show_error, get_config_from_args

try:
    import readline
except ImportError:
    pass

def tarbell_configure(args):
    """Tarbell configuration routine"""
    puts("Configuring Tarbell. Press ctrl-c to bail out!")

    path = get_config_from_args(args)

    _get_or_create_config_dir(path)

    settings = {}
    settings.update(_setup_google_spreadsheets(path))
    settings.update(_setup_s3(path))
    settings.update(_setup_tarbell_project_path(path))
    settings.update(_setup_default_templates(path))

    settings_path = os.path.join(path, "settings.yaml")
    _backup(path, "settings.yaml")

    with open(settings_path, "w") as f:
        puts("\nCreating {0}".format(colored.green(settings_path)))
        yaml.dump(settings, f, default_flow_style=False)

    puts("\n- Done configuring Tarbell. Type `{0}` for help.\n"
         .format(colored.green("tarbell")))

    return Settings(path)

def _get_or_create_config_dir(path):
    """Get or create a Tarbell configuration directory."""
    if (os.path.isdir(path)):
        puts("{0} already exists".format(colored.green(path)))
        overwrite = raw_input(("\nWould you like to reconfigure Tarbell? All "
                               "existing files will be backed up. [y/N] "
                             ))
        if overwrite.lower() != "y":
            puts("\n- Not overwriting existing Tarbell configuration. See ya!")
            sys.exit(1)

    else:
        create = raw_input(("\nWould you like to create a Tarbell configuration "
                            "in {0}? [Y/n] ".format(colored.green(path))
                          ))
        if create.lower() == "y" or create == "":
            os.makedirs(path)
        else:
            puts("\n- Not creating Tarbell configuration. See ya!")
            sys.exit(1)


def _setup_google_spreadsheets(path):
    """Set up a Google spreadsheet"""
    settings = {}

    use = raw_input("\nWould you like to use Google spreadsheets [Y/n]? ")
    if use.lower() == "y" or use == "":
        puts(("\nLogin in to Google and go to {0} to create an app and generate the "
              "\n{1} authentication file. You should create credentials for an `installed app`. See "
              "\n{2} for more information."
              .format(colored.red("https://code.google.com/apis/console/"),
                      colored.yellow("client_secrets.json"),
                      colored.red("http://tarbell.readthedocs.com/#correctlink")
                     )
            ))

        secrets_path = raw_input(("\nWhere is your client secrets file? "
                                  "[~/Downloads/client_secrets.json] "
                                ))

        if secrets_path == "":
            secrets_path = os.path.expanduser(os.path.join("~",
                                              "Downloads/client_secrets.json"
                                             ))
        puts("\nCopying {0} to {1}\n".format(colored.green("client_secrets.json"),
                                         colored.green(path))
            )

        _backup(path, "client_secrets.json")
        shutil.copy(secrets_path, path)

        # Now, try and obtain the API for the first time
        get_drive_api(path) #, reset_creds=True)

        account = raw_input(("What Google account should have access to new spreadsheets? "
                             "(e.g. somebody@gmail.com, leave blank to specify for each new "
                             "project) "
                            ))
        if account != "":
            settings.update({ "google_account" : account })

    else:
        puts(("No worries! Don't forget you'll need to configure your context "
              "variables in each project's {0} file."
              .format(colored.yellow("config.py"))
            ))

    puts("\n- Done configuring Google spreadsheets.")
    return settings


def _setup_s3(path, access_key=None, access_key_id=None):
    """Prompt user to set up Amazon S3"""
    use = raw_input("\nWould you like to set up Amazon S3? [Y/n] ")
    if use.lower() != "y" and use != "":
        puts("\n- Not configuring Amazon S3.")
        return {}

    puts("\nCalling s3cmd --configure\n")
    call(['s3cmd', '--configure'])

    buckets = {}

    staging = raw_input("\nWhat is your default staging bucket? (e.g. s3://apps.beta.myorg.com/, leave blank to skip) ")
    if staging != "":
        buckets.update({"staging": staging})

    production = raw_input("\nWhat is your default production bucket? (e.g. s3://apps.myorg.com/, leave blank to skip) ")
    if production != "":
        buckets.update({"production": production})

    puts("\n- Done configuring Amazon S3.")
    return {"s3_buckets": buckets}


def _setup_tarbell_project_path(path):
    """Prompt user to set up project path."""
    default_path = os.path.expanduser(os.path.join("~", "tarbell"))
    projects_path = raw_input("\nWhat is your Tarbell projects path? [Default: {0}, 'none' to skip] ".format(colored.green(default_path)))
    if projects_path == "":
        projects_path = default_path
    if projects_path.lower() == 'none':
        puts("\n- Not creating projects directory.")
        return {}

    if os.path.isdir(projects_path):
        puts("\nDirectory exists!")
    else:
        puts("\nDirectory does not exist.")
        make = raw_input("\nWould you like to create it? [Y/n] ")
        if make.lower() == "y" or not make:
            os.makedirs(projects_path)
    puts("\nProjects path is {0}".format(projects_path))
    puts("\n- Done setting up projects path.")
    return {"projects_path": projects_path}


def _setup_default_templates(path):
    """Add some (hardcoded) default templates."""
    project_templates = [{
        "name": "Basic Bootstrap 3 template",
        "url": "https://github.com/newsapps/tarbell-template",
    }, {
        "name": "Searchable map template",
        "url": "https://github.com/eads/tarbell-map-template",
    }]
    for project in project_templates:
        puts("+ Adding {0} ({1})".format(project["name"], project["url"]))

    puts("\n- Done configuring project templates.")
    return {"project_templates": project_templates}


def _backup(path, filename):
    """Backup a file."""
    target = os.path.join(path, filename)
    if os.path.isfile(target):
        dt = datetime.now()
        new_filename = "{0}.{1}.{2}".format(
            filename, dt.isoformat(), "backup"
        )
        destination = os.path.join(path, new_filename)
        puts("\n-- Backing up {0} to {1}\n".format(
            colored.cyan(target),
            colored.cyan(destination)
        ))

        shutil.copy(target, destination)
