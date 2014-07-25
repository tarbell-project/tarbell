=======================
Configuration reference
=======================

.. _tarbell-config:

Project settings (``tarbell_config.py``)
----------------------------------------

Each project has a ``tarbell_config.py`` file that controls settings for the project. These are
the possible configuration variables:

``NAME``
  Short name of project, such as 'myproject` (required)
``TITLE``
  Descriptive title of project, such as 'My award winning project` (required)
``EXCLUDES``
  A list of files to exclude from publication such as ``["*.txt", "img/mockup.psd"]`` (optional)
``CREATE_JSON``
  Boolean. If true, spreadsheet will be previewed and published as ``data.json`` (default: False)
``SPREADSHEET_CACHE_TTL``
  How long to cache spreadsheet values, in seconds (default: 4)
``SPREADSHEET_KEY``
  If provided, Tarbell will use a Google spreadsheet with this key for template context (optional)
``CONTEXT_SOURCE_FILE``
  If provided, Tarbell will use this data file for the template context. CSV, XLS, and XSLX files
  are supported. The value may use a relative path, an absolute path, or a remote (http) URL. (optional)
``CREDENTIALS_PATH``
  Path to a credentials file to authenticate with Google Drive.This is useful for for automated 
  deployment. Take care not to commit or publish your credentials file. (optional) (experimental:
  this option may be replaced by command line flag or environment variable)
``S3_BUCKETS``
  A dict of target->url pairs such as ``{ 'production': 'apps.myorg.com' }`` (required for publishing to S3)
``DEFAULT_CONTEXT``
  A dict of fallback values for the project context. Use this if you don't want or need a Google spreadsheet
  or external file.

Tarbell settings (``~/.tarbell/settings.yaml``)
--------------------------------------------------------------

The settings file uses a simple YAML-based format::

  default_s3_access_key_id: <DEFAULT KEY ID>
  default_s3_secret_access_key: <DEFAULT SECRET KEY>
  default_s3_buckets:
    production: apps.chicagotribune.com
    staging: apps.beta.tribapps.com
  google_account: davideads@gmail.com
  project_templates:
  - name: Basic Bootstrap 3 template
    url: https://github.com/newsapps/tarbell-template
  - name: Searchable map template
    url: https://github.com/eads/tarbell-map-template
  projects_path: /Users/davideads/tarbell
  s3_credentials:
    26thandcalifornia.recoveredfactory.net:
      access_key_id: <KEY ID>
      secret_access_key: <SECRET KEY>

This example shows every possible setting.

``google_account``
    Default Google account to use when creating new projects
``project_templates``
    A list of ``{name: ..., url: ...}`` objects with project templates.
``projects_path``
    Path to the user's Tarbell projects
``default_s3_access_key_id``
    Default key ID to use when publishing
``default_s3_secret_access_key``
    Default key to use when publishing
``default_s3_buckets``
    alias->s3 url pairs to be used during project creation for setting up default bucket aliases. These are only used during project creation and can be overridden on a per-project basis.
``s3_credentials``
    Define S3 credentials using a ``bucket-uri->{ access_key_id: ..., secret_access_key: ...}`` data strucutre. 

Google SDK client secrets (``~/.tarbell/client_secrets.json``)
--------------------------------------------------------------

Place a ``client_secrets.json`` file in ``~/.tarbell`` or use ``tarbell configure drive``.
