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
from tarbell import LONG_VERSION

from .settings import Settings
from .oauth import get_drive_api_from_client_secrets
from .utils import show_error


def tarbell_configure(command, args):
    """Tarbell configuration routine"""
    puts("Configuring Tarbell. Press ctrl-c to bail out!")

    # Check if there's settings configured
    settings = Settings()
    path = settings.path

    prompt = True
    if len(args):
        prompt = False

    config = _get_or_create_config(path)

    if prompt or "drive" in args:
        config.update(_setup_google_spreadsheets(config, path, prompt))
    if prompt or "s3" in args:
        config.update(_setup_s3(config, path, prompt))
    if prompt or "path" in args:
        config.update(_setup_tarbell_project_path(config, path, prompt))
    if prompt or "templates" in args:
        if "project_templates" in config:
            override_templates = raw_input("\nFound Base Template config. Would you like to override them? [Default: No, 'none' to skip]")
            if override_templates and override_templates != "No" and  override_templates != "no" and override_templates != "N" and override_templates != "n":
                config.update(_setup_default_templates(config, path, prompt))
            else:
                puts("\nPreserving Base Template config...")
        else:
            config.update(_setup_default_templates(config, path, prompt))


    with open(path, 'w') as f:
        puts("\nWriting {0}".format(colored.green(path)))
        settings.save()

    if all:
        puts("\n- Done configuring Tarbell. Type `{0}` for help.\n"
             .format(colored.green("tarbell")))

    return settings


def _get_or_create_config(path, prompt=True):
    """Get or create a Tarbell configuration directory."""
    dirname = os.path.dirname(path)
    filename = os.path.basename(path)

    try:
        os.makedirs(dirname)
    except OSError:
        pass

    try:
        with open(path, 'r+') as f:
            if os.path.isfile(path):
                puts("{0} already exists, backing up".format(colored.green(path)))
                _backup(dirname, filename)
            return yaml.load(f)
    except IOError:
        return {}


def _setup_google_spreadsheets(settings, path, prompt=True):
    """Set up a Google spreadsheet"""
    ret = {}
    if prompt:
        use = raw_input("\nWould you like to use Google spreadsheets [Y/n]? ")
        if use.lower() != "y" and use != "":
            return settings

    dirname = os.path.dirname(path)
    path = os.path.join(dirname, "client_secrets.json")

    write_secrets = True
    if os.path.isfile(path):
        write_secrets_input = raw_input("client_secrets.json already exists. Would you like to overwrite it? [y/N] ")
        if not write_secrets_input.lower().startswith('y'):
            write_secrets = False

    if write_secrets:
        puts(("\nLogin in to Google and go to {0} to create an app and generate a "
              "\nclient_secrets authentication file. You should create credentials for an `installed app`. See "
              "\n{1} for more information."
              .format(colored.red("https://console.developers.google.com/project"),
                      colored.red("http://tarbell.readthedocs.org/en/{0}/install.html#configure-google-spreadsheet-access-optional".format(LONG_VERSION))
                     )
            ))

        secrets_path = raw_input(("\nWhere is your client secrets file? "
                                  "[~/Downloads/client_secrets.json] "
                                ))

        if secrets_path == "":
            secrets_path = os.path.join("~", "Downloads/client_secrets.json")

        secrets_path = os.path.expanduser(secrets_path)

        puts("\nCopying {0} to {1}\n"
             .format(colored.green(secrets_path),
                     colored.green(dirname))
        )

        _backup(dirname, "client_secrets.json")
        try:
            shutil.copy(secrets_path, os.path.join(dirname, 'client_secrets.json'))
        except shutil.Error, e:
            show_error(str(e))

    # Now, try and obtain the API for the first time
    get_api = raw_input("Would you like to authenticate your client_secrets.json? [Y/n] ")
    if get_api == '' or get_api.lower().startswith('y'):
        get_drive_api_from_client_secrets(path, reset_creds=True)

    default_account = settings.get("google_account", "")
    account = raw_input(("What Google account(s) should have access to new spreadsheets? "
                         "(e.g. somebody@gmail.com, leave blank to specify for each new "
                         "project, separate multiple addresses with commas) [{0}] "
                            .format(default_account)
                        ))
    if default_account != "" and account == "":
        account = default_account
    if account != "":
        ret = { "google_account" : account }

    puts("\n- Done configuring Google spreadsheets.")
    return ret


def _setup_s3(settings, path, prompt=True):
    """Prompt user to set up Amazon S3"""
    ret = {'default_s3_buckets': {}, 's3_credentials': settings.get('s3_credentials', {})}

    if prompt:
        use = raw_input("\nWould you like to set up Amazon S3? [Y/n] ")
        if use.lower() != "y" and use != "":
            puts("\n- Not configuring Amazon S3.")
            return ret

    existing_access_key = settings.get('default_s3_access_key_id', None) or \
                          os.environ.get('AWS_ACCESS_KEY_ID', None)
    existing_secret_key = settings.get('default_s3_secret_access_key', None) or \
                          os.environ.get('AWS_SECRET_ACCESS_KEY', None)

    #import ipdb; ipdb.set_trace();

    access_key_prompt = "\nPlease enter your default Amazon Access Key ID:"
    if existing_access_key:
        access_key_prompt += ' [%s] ' % existing_access_key
    else:
        access_key_prompt += ' (leave blank to skip) '
    default_aws_access_key_id = raw_input(access_key_prompt)

    if default_aws_access_key_id == '' and existing_access_key:
        default_aws_access_key_id = existing_access_key


    if default_aws_access_key_id:
        secret_key_prompt = "\nPlease enter your default Amazon Secret Access Key:"
        if existing_secret_key:
            secret_key_prompt += ' [%s] ' % existing_secret_key
        else:
            secret_key_prompt += ' (leave blank to skip) '
        default_aws_secret_access_key = raw_input(secret_key_prompt)

        if default_aws_secret_access_key == '' and existing_secret_key:
            default_aws_secret_access_key = existing_secret_key

        ret.update({
            'default_s3_access_key_id': default_aws_access_key_id,
            'default_s3_secret_access_key': default_aws_secret_access_key,
        })

    # If we're all set with AWS creds, we can setup our default
    # staging and production buckets
    if default_aws_access_key_id and default_aws_secret_access_key:
        existing_staging_bucket = None
        existing_production_bucket = None
        if settings.get('default_s3_buckets'):
            existing_staging_bucket = settings['default_s3_buckets'].get('staging', None)
            existing_production_bucket = settings['default_s3_buckets'].get('production', None)

        staging_prompt = "\nWhat is your default staging bucket?"
        if existing_staging_bucket:
            staging_prompt += ' [%s] ' % existing_staging_bucket
        else:
            staging_prompt += ' (e.g. apps.beta.myorg.com, leave blank to skip) '
        staging = raw_input(staging_prompt)

        if staging == '' and existing_staging_bucket:
            staging = existing_staging_bucket
        if staging != "":
            ret['default_s3_buckets'].update({
                'staging': staging,
            })

        production_prompt = "\nWhat is your default production bucket?"
        if existing_production_bucket:
            production_prompt += ' [%s] ' % existing_production_bucket
        else:
            production_prompt += ' (e.g. apps.myorg.com, leave blank to skip) '
        production = raw_input(production_prompt)

        if production == '' and existing_production_bucket:
            production = existing_production_bucket
        if production != "":
            ret['default_s3_buckets'].update({
                'production': production,
            })


    more_prompt = "\nWould you like to add additional buckets and credentials? [y/N] "
    while raw_input(more_prompt).lower() == 'y':
        ## Ask for a uri
        additional_s3_bucket = raw_input(
            "\nPlease specify an additional bucket (e.g. "
            "additional.bucket.myorg.com/, leave blank to skip adding bucket) ")
        if additional_s3_bucket == "":
            continue

        ## Ask for an access key, if it differs from the default
        additional_access_key_prompt = "\nPlease specify an AWS Access Key ID for this bucket:"

        if default_aws_access_key_id:
            additional_access_key_prompt += ' [%s] ' % default_aws_access_key_id
        else:
            additional_access_key_prompt += ' (leave blank to skip adding bucket) '

        additional_aws_access_key_id = raw_input(additional_access_key_prompt)

        if additional_aws_access_key_id == "" and default_aws_access_key_id:
            additional_aws_access_key_id = default_aws_access_key_id
        elif additional_aws_access_key_id == "":
            continue

        # Ask for a secret key, if it differs from default
        additional_secret_key_prompt = "\nPlease specify an AWS Secret Access Key for this bucket:"

        if default_aws_secret_access_key:
            additional_secret_key_prompt += ' [%s] ' % default_aws_secret_access_key
        else:
            additional_secret_key_prompt += ' (leave blank to skip adding bucket) '

        additional_aws_secret_access_key = raw_input(
            additional_secret_key_prompt)

        if additional_aws_secret_access_key == "" and default_aws_secret_access_key:
            additional_aws_secret_access_key = default_aws_secret_access_key
        elif additional_aws_secret_access_key == "":
            continue

        ret['s3_credentials'][additional_s3_bucket] = {
            'access_key_id': additional_aws_access_key_id,
            'secret_access_key': additional_aws_secret_access_key,
        }

    puts("\n- Done configuring Amazon S3.")
    return ret


def _setup_tarbell_project_path(settings, path, prompt=True):
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


def _setup_default_templates(settings, path, prompt=True):
    """Add some (hardcoded) default templates."""
    project_templates = [{
        "name": "Basic Bootstrap 3 template",
        "url": "https://github.com/newsapps/tarbell-template",
    }, {
        "name": "Searchable map template",
        "url": "https://github.com/eads/tarbell-map-template",
    }, {
        "name": "Tarbell template walkthrough",
        "url": "https://github.com/hbillings/tarbell-tutorial-template",
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
        new_filename = ".{0}.{1}.{2}".format(
            filename, dt.isoformat(), "backup"
        )
        destination = os.path.join(path, new_filename)
        puts("- Backing up {0} to {1}".format(
            colored.cyan(target),
            colored.cyan(destination)
        ))

        shutil.copy(target, destination)
