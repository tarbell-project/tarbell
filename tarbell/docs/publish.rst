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

Configuring S3 buckets for a project
------------------------------------

As touched on in the
`Configuring projects section <build.html#configuring-projects>`_, you can
change the names and locations of your S3 buckets in the `tarbell_config.py`
file for a given project. Often, projects have a `staging` version for testing,
and a `production` version for the final product. However, these names are
entirely arbitrary, so you can pick anything you like.

As an example, let's say you have 3 versions of your site: one for testing, one
for the live site, and one that you'd like to preserve as an archive. They're
all kept as subdomains of tribapps.com, and your staging site actually houses
many different sites at various stages of development, so you want to publish
to a specific directory.

Create or update the `S3_BUCKETS` variable in `tarbell_config.py` as follows::

  S3_BUCKETS = {
      "staging": "staging.tribapps.com/tarbell-staging/",
      "production": "tarbell.tribapps.com/",
      "archive": "archive.tribapps.com/",
  }

To push your site to http://staging.tribapps.com/tarbell-staging, run::

  tarbell publish staging

To push your site to http://tarbell.tribapps.com, run::

  tarbell publish production

You're pretty smart (that's why you're using Tarbell), so you've probably
already figured out the pattern, but to push your site to
http://archive.tribapps.com, run::

  tarbell publish archive
