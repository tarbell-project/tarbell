=================
Publish a Project
=================
*Use fab deploy and fab project:<projectname> deploy to upload your project to
Amazon S3. Customize the publishing process.*

Amazon S3 setup
---------------

An Amazon S3 publishing workflow is included in the Tarbell template. To use
it, you'll need your `Amazon S3 credentials
<https://portal.aws.amazon.com/gp/aws/developer/account/index.html?action=access-key>`_.

Create a file called ``s3config.py`` in your Tarbell template directory.

::

    S3CONFIG = {
        'BUCKETNAME': {
            'bucket': 'mybucket.domain.com',
            'key': 'KEY',
            'key_id': 'KEYID',
        }
    }

Help! I don't have an Amazon S3 account.
----------------------------------------
Amazon S3 is simply online file storage -- think of it as FTP on steroids.
Setting up an Amazon S3 account is easy. Just check out `this beginners guide
<http://www.hongkiat.com/blog/amazon-s3-the-beginners-guide/>`_. If you want to
use your S3 "bucket" as a website, read Amazon's guide to `S3 website hosting
<http://docs.aws.amazon.com/AmazonS3/latest/dev/WebsiteHosting.html>`_.

Deploying
---------

Once your Amazon S3 access credentials are configured, deploying all projects is very simple:

::

    fab target:BUCKETNAME deploy

This will deploy to the bucket specified by BUCKETNAME in s3config.py.

To simplify deploying to the bucket named production, simply run:

::

    fab deploy

When deploying you'll see something like:

::

    [localhost] local: python render_templates.py 
    Rendering templates.

    Generating project 'base' in /Users/davideads/Repos/tarbell/out/
    -- No Google doc configured for base.

    Generating project 'readme' in /Users/davideads/Repos/tarbell/out/readme
    -- Created JSON /Users/davideads/Repos/tarbell/out/readme/json/values.json
    -- Created JSON /Users/davideads/Repos/tarbell/out/readme/json/LAST_UPDATED.json
    -- Created JSON /Users/davideads/Repos/tarbell/out/readme/json/projects.json
    -- Created page /Users/davideads/Repos/tarbell/out/readme/index.html

    [localhost] local: python s3deploy.py
    Deploying to tarbell.tribapps.com
    Uploading css/style.css
    Uploading js/app.js
    Uploading js/templates/nav.jst
    Uploading js/views/NavigationView.js
    Uploading readme/index.html
    Refreshing Facebook info for: http://tarbell.tribapps.com/readme/index.html?fbrefresh=CANBEANYTHING
    Uploading readme/bootstrap/css/bootstrap.css
    Uploading readme/bootstrap/css/bootstrap.min.css
    Uploading readme/bootstrap/img/glyphicons-halflings-white.png
    Uploading readme/bootstrap/img/glyphicons-halflings.png
    Uploading readme/bootstrap/js/bootstrap.js
    Uploading readme/bootstrap/js/bootstrap.min.js
    Uploading readme/css/ir_black.css
    Uploading readme/css/style.css
    Uploading readme/img/google-screenshot.jpg
    Uploading readme/img/html-edit-screenshot.jpg
    Uploading readme/img/ida-tarbell.jpg
    Uploading readme/img/s3-publish-screenshot.jpg
    Uploading readme/js/app.js
    Uploading readme/json/LAST_UPDATED.json
    Uploading readme/json/projects.json
    Uploading readme/json/values.json

To deploy a specific project, use the ``project:PROJECTNAME`` flag:

::

    fab project:PROJECTNAME deploy

In the following example, we'll publish a project called ``basketball`` using a
bucket configuration named ``sports``:

::

    fab project:basketball target:sports deploy

**Please note**: The base template is always published -- it is assumed most
projects will use some base components.
