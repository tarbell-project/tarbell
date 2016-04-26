==========
Publishing
==========

Generate static sites with ``tarbell generate``
----------------------------------------------------------------

Generate HTML in a specific directory::

  tarbell generate ~/output/myproject

If output directory is not specified, Tarbell will raise an error asking for one.

.. note::

  ``tarbell generate`` can be used to manually publish sites to hosts other than Amazon. Write a
  simple deployment script or use Fabric to call ``tarbell generate <mydirectory>`` and invoke a
  command to sync ``<mydirectory>`` with your host.

Publish projects with ``tarbell publish <target>``
---------------------------------------------------------------------

If Amazon S3 is configured, you can publish with::

  tarbell publish <bucketname>

The default bucket is ``staging``.

You can specify a bucket when publishing (defined in ``tarbell_config.py``)::

  tarbell publish production

Configuring S3 buckets for a project
------------------------------------

As touched on in the
`Configuring projects section <build.html#configuring-projects>`_, you can
change the names and locations of your S3 buckets in the ``tarbell_config.py``
file for a given project. Often, projects have a ``staging`` version for testing,
and a ``production`` version for the final product. However, these names are
entirely arbitrary, so you can pick anything you like.

As an example, let's say you have 3 versions of your site: one for testing, one
for the live site, and one that you'd like to preserve as an archive. They're
all kept as subdomains of tribapps.com, and your staging site actually houses
many different sites at various stages of development, so you want to publish
to a specific directory.

This example assumes the same AWS ID and secret access key can be used to authenticate
with each of the targets.

Create or update the ``S3_BUCKETS`` variable in ``tarbell_config.py`` as follows:

.. code-block:: python

  S3_BUCKETS = {
      "staging": "staging.tribapps.com/tarbell-staging",
      "production": "tarbell.tribapps.com",
      "archive": "archive.tribapps.com",
  }

To push your site to http://staging.tribapps.com/tarbell-staging, run::

  tarbell publish staging

To push your site to http://tarbell.tribapps.com, run::

  tarbell publish production

You've probably already figured out the pattern, but to push your site to
http://archive.tribapps.com, run::

  tarbell publish archive

.. note::

    The preferred format for S3 buckets is demonstrated above, without an ``s3://`` protocol
    indicator or trailing slash. However, ``s3://foo.com/bar/`` will work as well.


Handling buckets with differing credentials
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

What if ``archive.tribapps.com`` uses different Amazon S3 credentials?

To handle buckets with non-default credentials, run ``tarbell configure`` and configure
a new bucket::

  Please specify an additional bucket (e.g. additional.bucket.myorg.com/, leave blank to skip adding bucket) archive.tribapps.com

  Please specify an AWS Access Key ID for this bucket: [XXXXXXXXX] XXXXXXXXX

  Please specify an AWS Secret Access Key for this bucket: [XXXXXXXXX] XXXXXXXXX

Or add some lines to ``~/.tarbell/settings.yaml``::

  # ...
  s3_credentials:
    foo.bar.com:
      access_key_id: XXXXXXXX
      secret_access_key: XXXXXXXXXXXX

You can now publish to a bucket with non-default access credentials.

Tarbell does not delete files on S3
-----------------------------------

Because altering Amazon S3 buckets has some inherent dangers, Tarbell 1.0 does not include
a delete feature. You can manually delete files on Amazon through the
`web interface <https://console.aws.amazon.com/>`_ or with a client like
`Cyberduck <https://cyberduck.io/?l=en>`_.
