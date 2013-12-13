==========
Publishing
==========

Manually publish projects with `tarbell generate <output_dir>`
--------------------------------------------------------------

Generate HTML in a temporary directory::

  tarbell generate

Generate HTML in a specific directory::

  tarbell generate ~/output/myproject


Publish projects with `tarbell publish <staging/production/target>`
-------------------------------------------------------------------

If Amazon S3 is configured, you can publish with::

  tarbell publish

The default bucket is `staging`.

You can specify a bucket when publishing (defined in `tarbell_config.py`)::

  tarbell publish production

Remove projects with `tarbell unpublish <staging/production/target>`
--------------------------------------------------------------------

Not implemented.
