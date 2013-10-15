================
Tarbell tutorial
================

Let's build a website about Ida Tarbell! 

First you need Tarbell. Fair warning, you're going to have to run these commands in
a terminal::

    pip install tarbell

(Don't know how to install pip? <resource-tk> can help!)

Got it? Now configure Tarbell::

    tarbell configure

For our tutorial, just say "no" to drugs and to configuring Google or Amazon. It's optional!::

  Configuring Tarbell. Press ctrl-c to bail out!

  Would you like to create a Tarbell configuration in /Users/davideads/.tarbell? [Y/n] Y

  Would you like to use Google spreadsheets [Y/n]? n
  No worries! Don't forget you'll need to configure your context variables in each project's config.py file.

  - Done configuring Google spreadsheets.

  Would you like to set up Amazon S3? [Y/n] n

  - Not configuring Amazon S3.

  What is your Tarbell projects path? [Default: /Users/davideads/tarbell, 'none' to skip] 

  Directory exists!

  Projects path is /Users/davideads/tarbell

  - Done setting up projects path.
  + Adding Basic Bootstrap 3 template (https://github.com/newsapps/tarbell-template)
  + Adding Searchable map template (https://github.com/eads/tarbell-map-template)

  - Done configuring project templates.

  Creating /Users/davideads/.tarbell/settings.yaml

  - Done configuring Tarbell. Type `tarbell` for help.

Now that you've got Tarbell configured, create a new project::

  tarbell newproject


