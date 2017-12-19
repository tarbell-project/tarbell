============
Installation
============

Install Tarbell with `pip install tarbell`
------------------------------------------

.. code-block:: bash

    pip install tarbell

.. note::

  Tarbell requires Python 2.7 or 3.4+ and Git (v1.5.2+).

  Tarbell does not (yet) work on Windows machines.

  To install on Ubuntu (tested with Ubuntu 14.04 LTS), install these dependencies first:

  .. code-block:: bash

      apt-get install build-essential git python-pip python-dev libncurses5-dev

  To install with Fedora 21, install these dependencies from Edward Borasky's `Tarbell docker image <https://registry.hub.docker.com/u/znmeb/osjourno-tarbell/dockerfile/>`_ (untested).

  .. code-block:: bash

    yum install gcc git libyaml-devel make patch python-devel python-pip readline-devel tar


Configure Tarbell with `tarbell configure`
------------------------------------------

The ``tarbell configure`` command will set up your Tarbell settings

.. code-block:: bash

  tarbell configure

Please consider setting up Google spreadsheet access for collaborative data editing and Amazon
S3 settings for easy publishing.


Configure Google spreadsheet access (optional)
----------------------------------------------

In order to allow Tarbell to create new Google Spreadsheets, you'll need to
download a `client_secrets.json file <https://developers.google.com/api-client-library/python/guide/aaa_client_secrets>`_
to access the Google Drive API. You can share this file with collaborators and
within your organization, but do not share this file anywhere public.

Log in to the `Google API Developer Console <https://cloud.google.com/console/project>`_ and create a new project:

.. image:: /img/install__new_project_button.png
   :width: 700px

Enter a project name in the pop-up dialog and click the "Create" button:

.. image:: /img/install__new_project_dialog.png
   :width: 700px

The project will be created and you'll be taken to the project dashboard.

Click the "Google APIs" tab and then click on the "Drive API" link:

.. image:: /img/install__click_drive_api.png
   :width: 700px

Click the "Enable API" button:

.. image:: /img/install__click_enable_api.png
   :width: 700px

Click the "Credentials" item in the sidebar:

.. image:: /img/install__click_credentials.png
   :width: 700px

Click the "New credentials" button and select the "OAuth client ID" item from the drop-down menu:

.. image:: /img/install__click_new_credentials.png
   :width: 700px

You'll need to configure the consent screen before you can create the credentials.  Click the "Configure consent screen" button to configure the consent screen:

.. image:: /img/install__click_configure_consent_screen.png
   :width: 700px

Fill out the required fields of the consent screen form and then click the "Save" button:

.. image:: /img/install__configure_consent_screen.png
   :width: 700px

Once the consent screne is configured, you'll be asked to create the client ID.  Select the "Other" for "Application type", specify a name for the client and click the "Create" button:

.. image:: /img/install__create_client_id.png
   :width: 700px

You will be shown the client ID and client secret in a popup window.  Click the OK button, and you will be shown a list of client IDs.  Click the download icon next to the client ID you just created to download the ``client_secrets.json`` file: 

.. image:: /img/install__download_credentials.png
   :width: 700px

The file you download will be called something like 
``client_secret_longstringofrandomlettersandnumbers.apps.googleusercontent.json``.

Rename it to ``client_secrets.json``.

Now, you do one of the following:

* Copy ``client_secrets.json`` to ``~/.tarbell/client_secrets.json``.
* Specify the ``client_secrets.json`` download location when running ``tarbell configure``. (By default, Tarbell will attempt to find this file in your ``Downloads`` directory.)

The first time a Tarbell command needs access to a Google spreadsheet (say, while you're running `tarbell configure`), you'll be prompted to
authenticate

.. code-block:: bash

  Go to the following link in your browser:

      https://accounts.google.com/o/oauth2/auth?scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&response_type=code&client_id=705475625983-bdm46bacl3v8hlt4dd9ufvgsmgg3jrug.apps.googleusercontent.com&access_type=offline

  Enter verification code: 

Follow the link:

.. image:: /img/create_7_new.png

You should receive a confirmation code:

.. image:: /img/create_8.png


Enter it. If it works, you'll see:

  Authentication successful.

Now you can access and create Google spreadsheets to use with Tarbell projects.

.. note::

    You need to visit the authentication page from the same machine that you are configuring Tarbell
    in order to avoid an OAuth Error. If you are using a remote machine, consider using the Lynx terminal 
    browser. Alternatively, you can `pre-authenticate <remote-configuration.rst>`.

Configure Amazon S3
-------------------

Generate keys for your Amazon S3 account. Add them during the Amazon S3 section of installation.

To generate keys, log into your `AWS Console <http://aws.amazon.com/>`_, click your name and select
"Security Credentials".

.. image:: /img/aws_security_creds.png
   :width: 700px


Don't worry about IAM users right now.

.. image:: /img/aws_continue.png
   :width: 700px


You should see a list of different sections. Click the section that reads, 
"Access Keys (Access Key ID and Secret Access Key)" and then the button, "Create New Access Key."
Note that if you have existing keys, you can currently retrieve its Access Key ID 
and Secret Access Key from the legacy Security Credentials page (linked to in this section), 
but that Amazon plans to remove the ability to see this information soon.

.. image:: /img/aws_create_new_key.png
   :width: 700px


Woohoo, now you can download your keys! You MUST do this now -- Amazon only lets you download 
the keys on this screen. If you accidentally close the prompt, you can always delete the 
keys you just generated and generate a new pair.

.. image:: /img/aws_download_keys.png
   :width: 700px

Now you need to tell Tarbell what your AWS keys are. Run `tarbell configure`. After it checks to see if Google is configured, you'll get this prompt::

  Would you like to set up Amazon S3? [Y/n] y

  Please enter your default Amazon Access Key ID: (leave blank to skip)

  Please enter your default Amazon Secret Access Key: (leave blank to skip)

  What is your default staging bucket? (e.g. apps.beta.myorg.com, leave blank to skip)

If you don't already have a staging or production bucket, you can create one by 
going to the S3 management console and clicking "Create bucket."

.. image:: /img/aws_create_bukkits.png
   :width: 700px

.. image:: /img/aws_bukkit_settings.png
   :width: 700px

Just remember that when you name a bucket, it must be unique to AWS, not just your account. 
Like usernames, bucket names are shared across the entire Amazon system. (Which is silly, but 
that's how it is.)

.. image:: /img/aws_bukkit_settings.png
   :width: 700px

Once you've added production and staging buckets to your configuration, you will get this message::

  Would you like to add bucket credentials? [y/N]

If there are additional buckets in your S3 account that you want to use with Tarbell, enter
their names here. Otherwise, skip this.

Set a default project path
--------------------------

This is where your Tarbell projects will live. This path will be used by `tarbell list` 
and `tarbell switch`.

.. image:: /img/project_path.png
   :width: 700px

Using Tarbell with virtualenv
-----------------------------

.. note::
 
  If you've never heard of virtualenvs or know you're not using one with
  Tarbell, skip this section.

Virtual environments (`virtualenv <http://www.virtualenv.org/>`_) are useful for
developers and advanced users managing many Python packages. Tarbell can be installed
globally or within a virtualenv.

If you'll be working on Tarbell itself, extending its functionality
or otherwise manipulating the guts of the system, then it might make sense to
install it inside a virtualenv.

Here are some things to keep in mind if you use a virtualenv:

* The Tarbell settings file ``(~/.tarbell/settings.yaml)`` is global, meaning all
  Tarbell projects - whether inside a virtualenv or not - share the same
  settings. This includes the path that Tarbell expects to find all your
  projects (i.e., where Tarbell will look when you run ``tarbell list`` and
  ``tarbell switch``.)
* The ``client_secrets.json`` file used to authenticate to Google is also global,
  so you may run into problems using multiple Google accounts to access spreadsheets.

