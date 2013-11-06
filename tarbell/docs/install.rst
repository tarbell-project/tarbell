===============
Install Tarbell
===============

Install Tarbell with `pip install tarbell`
------------------------------------------

::

    pip install tarbell==0.9b2


Configure Tarbell with `tarbell configure`
------------------------------------------

The `tarbell configure` command will set up your Tarbell settings::

  tarbell configure

Please consider setting up Google spreadsheet access for collaborative data editing and Amazon
S3 settings for easy publishing.


Configure Google spreadsheet access (optional)
----------------------------------------------

In order to allow Tarbell to create new Google Spreadsheets, you'll need to
download a `client_secrets.json file
<https://developers.google.com/api-client-library/python/guide/aaa_client_secrets>`_
to access the Google Drive API. You can share this file with collaborators and
within your organization, but do not share this file anywhere public.

Log in to the `Google API Developer Console
<https://code.google.com/apis/console/>`_ and create a new project:

.. image:: create_1.png
   :width: 700px

Now click the "Services" tab and enable Google Drive API.

.. image:: create_2.png
   :width: 700px

Click the "API Access" tab to create a client ID:

.. image:: create_3.png
   :width: 700px

Add some project details. These don't really matter:

.. image:: create_4.png
   :width: 700px

This is the important screen. Select "installed app" and "other":

.. image:: create_5.png
   :width: 700px

Whew! Now you can download the ``client_secrets.json`` file:

.. image:: create_6.png
   :width: 700px

Copy `client_secrets.json` to `~/.tarbell/client_secrets.json` or specify the download
location when running `tarbell configure`.

The first time a Tarbell command needs access to a Google spreadsheet, you'll be prompted to
authenticate::

  Go to the following link in your browser:

      https://accounts.google.com/o/oauth2/auth?scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&response_type=code&client_id=705475625983-bdm46bacl3v8hlt4dd9ufvgsmgg3jrug.apps.googleusercontent.com&access_type=offline

  Enter verification code: 

Follow the link:

.. image:: create_7.png
   :width: 700px

You should receive a confirmation code:

.. image:: create_8.png

Enter it. If it works, you'll see:

  Authentication successful.

Now you can access and create Google spreadsheets to use with Tarbell projects.

Configuring Amazon S3
---------------------

Learn how to `set up Amazon S3 <http://www.smalldatajournalism.com/projects/one-offs/using-amazon-s3/>`_ in
the Small Data Journalism guide.

Configure `s3cmd`::

  s3cmd --configure

`tarbell configure` will do this for you::

  Would you like to set up Amazon S3? [Y/n] y

  Calling s3cmd --configure

  <s3cmd output, be sure to answer y at the end>

  What is your default staging bucket? (e.g. s3://apps.beta.myorg.com/, leave blank to skip) s3://projects.beta.coolorg.net/

  What is your default production bucket? (e.g. s3://apps.myorg.com/, leave blank to skip) s3://projects.coolorg.net/

  - Done configuring Amazon S3.




