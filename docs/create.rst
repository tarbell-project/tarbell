===========================
Create and install projects
===========================

.. note::

    Tarbell requires Git to install project and blueprints and does not support interactive Git sessions. If Git attempts to open an interactive prompt when accessing a private repository via HTTPS, Tarbell will exit with a warning.


Create a new project with `tarbell newproject <projectname>`
------------------------------------------------------------

Run

.. code-block:: bash

    tarbell newproject

You'll be asked a few questions, such as which path you'd like to create the project on, 
whether you want to use Google spreadsheets, and whether you want to instantiate a git repo. 
(See the tutorial for more details.)

When you're done, run a preview server

.. code-block:: bash

    tarbell switch myprojectname

You can now open up `/path/to/myprojectname` and start editing the "index.html"
file.


Install an existing project with `tarbell install <repository-url>`
-------------------------------------------------------------------

.. note::

  The project must include a tarbell_config.py file and be able to be cloned with Git.
  If the project uses Google spreadsheets, your Google account must be able to access
  the spreadsheet in question.

Run

.. code-block:: bash

  tarbell install https://urltorepository.com/projectname

e.g.

.. code-block:: bash

  tarbell install https://github.com/sc3/crime-punishment
