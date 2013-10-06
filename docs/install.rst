===============
Install Tarbell
===============

Install Tarbell with `pip install tarbell`
------------------------------------------

::

    pip install tarbell

Set up Google Drive access (optional)
-------------------------------------

This step is recommended but optional.

Set up Amazon S3 buckets (optional)
----------------------------------

If you don't want an Amazon S3 bucket, you'll need to upload your files yourself.
See the tarbell generate documentation for more.

Configure Tarbell with `tarbell configure`
------------------------------------------

::

  tarbell configure

You'll be prompted to answer some questions:

::

    Would you like to use Google spreadsheets [Y/n]? Y

    <if n>
    No worries! Don't forget you'll need to configure your context variables
    in your projects' config.py files.

    <if Y>
    Login in to Google and go to https://code.google.com/apis/console/ to create
    an app and generate the client_secrets.json authentication file. You should
    create an "installed app" authentication file. See 
    http://tarbell.readthedocs.com/#correctlink for more information.

    Where is your client secrets file? [~/Downloads/client_secrets.json]
    <if exists>
    Copying client secrets to .tarbell/client_secrets.json. Authenticating your app..

    <if not exists>
    That file doesn't exist. Try again? You can always do this later. [Y/n] Y
    Where is your client secrets file? [~/Downloads/client_secrets.json]

    <Google docs workflow>

    <if google docs>
    Please specify a default Google account (such as somebody@gmail.com) that 
    will have access to created spreadsheets. Leave blank to specify for every 
    new project. 

    What is your default staging Amazon S3 path (such as s3://mybucket.beta.myorg.com/projects) [leave blank to skip]
    What is your default production Amazon S3 path (such as s3://mybucket.myorg.com/projects) [leave blank to skip]

    Would you like to use the default Tarbell example projects? [Y/n]

    <if n>
    No problem. You'll need to register some project templates once you're done
    using the `tarbell template add <template name> <template_repo>` 
    (e.g.`tarbell template add "Searchable map" https://github.com/newsapps/tarbell-searchable-map`).

    <if Y>
    Adding default Tarbell example projects...

    Lastly, where will your Tarbell projects be stored? This directory will be created if it doesn't exist. [~/tarbell/]


Now you're ready to create a project...
