================
Tutorial
================

Let's build a website about celebrated Chicago journalist Ethel Payne!

You'll need to have access to a command prompt (an application on your computer
that allows you to execute text-based commands). On a Mac, search for the Terminal application.
On a PC, search for the Command Prompt program. All of the commands we'll show you here
will need to be typed into the command prompt.

First you need to `install <install.html>`_ and `configure <install.html#configure-tarbell-with-tarbell-configure>`_
Tarbell. (Make sure to set up a Google spreadsheet.) Go ahead. We'll wait.

Step 1: Set up a new project
==============

After you've got Tarbell configured, create a new project by typing this command into your prompt::

  tarbell newproject

You'll need to answer a few questions. It will go something like this::

  tarbell newproject

  What is the project's short directory name? (e.g. my_project) ethelpayne

  Where would you like to create this project? [/Users/davideads/tarbell/ethelpayne] 

  What is the project's full title? (e.g. My awesome project) Ethel Payne: A life in journalism

  Pick a template

    [1] Basic Bootstrap 3 template
        https://github.com/newsapps/tarbell-template

    [2] Searchable map template   
        https://github.com/eads/tarbell-map-template

  Which template would you like to use? [1] 1

  Cloning into '_base'...

  Checking connectivity... done

  client_secrets found. Would you like to create a Google spreadsheet? [Y/n] y

  What Google account should have access to this this spreadsheet? (Use a full email address, such as your.name@gmail.com or the Google account equivalent.)

  Success! View the spreadsheet at https://docs.google.com/spreadsheet/your_key_will_go_here

  Copying configuration file

  - Creating tarbell.py project configuration file

  - Done copying configuration file

  Copying html files...
  Copying index.html to /Users/davideads/tarbell/ethelpayne

  Initial commit

  [master (root-commit) 2bf96fb] Created ethelpayne from https://github.com/newsapps/tarbell-template
  5 files changed, 58 insertions(+)
  create mode 100644 .gitignore
  create mode 100644 .gitmodules
  create mode 160000 _base
  create mode 100644 index.html
  create mode 100644 tarbell_config.py

  -- Calling newproject hooks --
  --- Calling create_repo
  Want to create a Github repo for this project [Y/n]? n
  Not creating Github repo...

  All done! To preview your new project, type:

  tarbell switch ethelpayne

  or

  cd /Users/davideads/tarbell/ethelpayne
  tarbell serve

  You got this!

Well, you heard the machine, you got this. Run the switch command to fire up a preview server::

  tarbell switch ethelpayne

::

  Switching to ethelpayne
  Edit this project's templates at /Users/davideads/tarbell/ethelpayne
  Running preview server...

  Press ctrl-c to stop the server
   * Running on http://127.0.0.1:5000/
   * Restarting with reloader

Now visit http://127.0.0.1:5000/ in a browser.

(You can also run your project by changing to the directory you created for it and running tarbell serve.)

You're ready to start editing your template.

Step 2: Add content
===========

In a browser, open the Google spreadsheet that you created during the project set up.
This is where our website's content will live. You'll see three worksheets: *values*,
*data* and *keyed_data*. Let's look at the values worksheet first.
You should see something like this:

[IMAGE]

Keys and values are a common idea in programming: each key is shorthand for a corresponding value.
Each of the values in the *values* column is available to your site when you use
the matching *key* in your template.

.. note::
Header fields that start with underscores, like *_notes* does here, will not be made
available to your template.

Open your project's index.html page and find this line::

    <h1>{{ headline }}</h1>

.. note::

To start creating pages, you'll need a text editor. (`Notepad++<http://notepad-plus-plus.org/download/v6.6.1.html>`_ is a
good starter editor for Windows, while `TextWrangler<http://www.barebones.com/products/textwrangler/>`_ is a
good one for Macs.)

Look at your page in the browser again and notice the headline matches what's
in your Google spreadsheet under the *value* column with the *key* "headline".
Try changing that value in the spreadsheet to "Ethel Payne, Chicago journalist".

Reload the server at http://127.0.0.1:5000 in your web browser to see your changes!

You can add as many keys and values as you like. We'll add a few.

[IMAGE]

Now we need to reference these variables in the template. Go back to index.html and add::

  <blockquote>{{ quote }}</blockquote>
  <p>from {{ quote_source }}</p>

Reload your site and look at the results!

.. note::

  Tarbell uses `Jinja2<http://jinja.pocoo.org/>`_ for templating. Read the `excellent documentation<http://jinja.pocoo.org/docs/>`_ to learn more about using Jinja.

Displaying data
===============

TK

Adding CSS
==========

TK

Using Javascript
===============

TK

