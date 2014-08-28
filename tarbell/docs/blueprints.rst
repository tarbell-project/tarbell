=============================
Developing Tarbell blueprints
=============================

Tarbell blueprints are starting points for your projects. They allow you
and your collaborators to take the tedium out of creating similar projects
over and over.

For example, your organization could use a Tarbell blueprint for
all mapping projects that includes all the common libraries, your organization's
branding, and default data to get started.

---------------------------
Basic blueprint ingredients
---------------------------

All Tarbell blueprints must include a file named ``blueprint.py``. At bare minimum, this file 
must include a variable called ``NAME``:

.. code-block:: python

  NAME = "My Tarbell blueprint"

Most Tarbell blueprints will want to define some standard files:

- ``_base.html``: This can be named whatever you want. It is the Jinja base template
  the rest of your templates should extend with ``{% extends '_base.html' %}``.
- ``index.html``: A default page to use as a starting point for project development.
- ``_spreadsheet.xlsx``: This Excel file is used to create the default Google spreadsheet
  your project will use.


----------------------------
Adding filters and functions
----------------------------

All Tarbell blueprints (and projects) can define
`Flask blueprints <http://flask.pocoo.org/docs/0.10/blueprints/>`
in order to add filters, context functions, and custom routes.

To enable this functionality, add to ``blueprint.py``:

.. code-block:: python

  from flask import Blueprint

  NAME = "My Tarbell blueprint"
  blueprint = Blueprint("base", __name__)

.. note::

  The ``"base"`` argument above is an arbitrary, unique name for the Flask blueprint. It can be
  anything, but you should stick with "base" for most blueprints. Same with the ``blueprint``
  variable name.

Now you can do anything a Flask blueprint can do, such as define a template filter. Here's a simple
example:

.. code-block:: python

  from flask import Blueprint
  from jinja2 import Markup

  NAME = "My Tarbell blueprint"
  blueprint = Blueprint("base", __name__)

  @blueprint.app_template_filter()
  def embiggen(text):
      return Markup('<div class="embiggen">{0}</div>'.format(text))

Now you can use the ``{{ myvariable|embiggen }}`` in your templates to wrap the output of 
``myvariable`` in a special ``div`` tag.

------------------
Implementing hooks
------------------

Tarbell blueprints can also implement Tarbell's hooks. For example, to print an cheery
message after creating a new project:

.. code-block:: python

  from tarbell.hooks import register_hook

  NAME = "My Tarbell blueprint"

  @register_hook("newproject")
  def cheery_message(site, git):
      print("You created a new project! Keep saving journalism and make us proud.")

A common use case for such a hook in the real world is to create a new repository in your
organization's version control system and set up default tickets.

---------------------
Handling requirements
---------------------

Tarbell blueprints can include a ``requirements.txt`` file in the same format used by ``pip``.
These requirements will be installed when the Tarbell blueprint or a project that uses it is
installed.


