=======================
Configuration reference
=======================

Tarbell settings (`~/.tarbell/settings.yaml`)
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

- `google_account`: Default Google account to use when creating new projects
- `project_templates`: A list of `{name: ..., url: ...}` objects with project templates.
- `projects_path`: Path to the user's Tarbell projects
- `default_s3_access_key_id`: Default key ID to use when publishing
- `default_s3_secret_access_key`: Default key to use when publishing
- `default_s3_buckets`: alias->s3 url pairs to be used during project creation for setting up default bucket aliases. These are only used during project creation and can be overridden on a per-project basis.
- `s3_credentials': Define S3 credentials using a `bucket-uri->{ access_key_id: ..., secret_access_key: ...}` data strucutre. 

Google SDK client secrets (`~/.tarbell/client_secrets.json`)
-----------------------------------------------------------------

Place a `client_secrets.json` file in `~/.tarbell` or use `tarbell configure drive`.
