=======================
Configuration reference
=======================

Simple configuration with the `tarbell configure` command
---------------------------------------------------------

Manually configure Tarbell settings in `~/.tarbell/config.yaml`
--------------------------------------------------------------

::

    projects_dir: /path/to/tarbell/projects
    google_account: googleaccount@gmail.com
    s3:
      access_key: accesskey
      access_key_id: accesskeyid
      staging_bucket: s3://s3bucketurl
      production_bucket: s3://s3bucketurl
    templates:
      - ['Basic Bootstrap 3.x Tarbell project', 'https://github.com/newsapps/tarbell-template']
      - ['Searchable map with Fusion Tables', 'https://github.com/eads/tarbell-searchable-map'] 


Use Google Drive SDK by creating `~/.tarbell/client_secrets.json`
-----------------------------------------------------------------

Configure new project creation and installation with `~/.tarbell/hooks.py`
--------------------------------------------------------------------------

`after_install_template()`
==========================

`after_install_project()`
=========================




