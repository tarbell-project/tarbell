============
Installation
============

Install Tarbell with `pip install tarbell`
------------------------------------------

::

    pip install tarbell==0.9b4


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
<https://cloud.google.com/console/project>`_ and create a new project:

.. image:: create_1_new.png
   :width: 700px
.. image:: create_1.5_new.png
   :width: 700px

Now click the "APIs & auth" tab. (Click on the "APIs" tab below that if it 
doesn't open automatically.) Enable Google Drive API.

.. image:: create_2_new.png
   :width: 700px

You'll also want to ensure that BigQuery API, Google Cloud SQL, Google Cloud 
Storage and Google Cloud Storage JSON API are enabled. (They should be by default, 
but things will break if they aren't.)

.. image:: create_2.5_new.png
   :width: 700px

Click the "Credentials" tab (right below "APIs") to create a client ID:

.. image:: create_3_new.png
   :width: 700px

This is the important screen. Select "installed app" and "other":

.. image:: create_5_new.png
   :width: 700px

Whew! Now you can download the ``client_secrets.json`` file:

.. image:: create_6_new.png
   :width: 700px

The file you download will be called something like 
`client_secret_longstringofrandomlettersandnumbers.apps.googleusercontent.json`. 
Rename it to `client_secrets.json`. Now, you do one of the following:
* Copy `client_secrets.json` to `~/.tarbell/client_secrets.json`
* Specify the `client_sercret.json` download location when running `tarbell configure`. 
  (Tarbell should be able to figure out where the file is automatically when 
  you configure it.)

The first time a Tarbell command needs access to a Google spreadsheet (say, while you're running `tarbell configure`), you'll be prompted to
authenticate::

  Go to the following link in your browser:

      https://accounts.google.com/o/oauth2/auth?scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&response_type=code&client_id=705475625983-bdm46bacl3v8hlt4dd9ufvgsmgg3jrug.apps.googleusercontent.com&access_type=offline

  Enter verification code: 

Follow the link:

.. image:: create_7_new.png
   :width: 700px

You should receive a confirmation code:

.. image:: create_8.png

Enter it. If it works, you'll see:

  Authentication successful.

Now you can access and create Google spreadsheets to use with Tarbell projects.

Configure Amazon S3
-------------------

Generate keys for your Amazon S3 account. Add them during the Amazon S3 section of installation.

Set a default project path
--------------------------

This path will be used by `tarbell list` and `tarbell switch`.

Set up project templates
------------------------

Work in progress.
