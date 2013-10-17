=======================
Configuration reference
=======================

Tarbell settings (`~/.tarbell/settings.yaml`)
--------------------------------------------------------------

The settings file uses a simple YAML-based format::

  google_account: googleaccount@gmail.com
  projects_path: /Users/davideads/tarbell
  project_templates:
  - name: Basic Bootstrap 3 template
    url: https://github.com/newsapps/tarbell-template
  - name: Searchable map template
    url: https://github.com/eads/tarbell-map-template
  s3_buckets:
    production: s3://projects.coolorg.net/
    staging: s3://projects.beta.coolorg.net/

Google SDK client secrets (`~/.tarbell/client_secrets.json`)
-----------------------------------------------------------------

Place the client secrets file in `~/.tarbell`.
