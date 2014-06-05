=================
Building projects
=================

Creating and editing templates
------------------------------

Tarbell projects consist of text files that may use `Jinja2 <http://jinja.pocoo.org/docs/>`_ templating features and any static assets.

If you create a file in your project directory called ``chapter1.html``, you'll be able to preview the file at http://localhost:5000/chapter1.html and publish to the same file. This file can be straight up HTML, or it can inherit from a Tarbell base template file. 

Files and directories that start with an underscore (``_``) or a dot (``.``), like the ``_blueprint`` directory containing the Tarbell blueprint files, will not be rendered by the preview server or included in the generated static HTML.


Understanding Tarbell blueprints
--------------------------------

Tarbell blueprints provide a foundation for building projects. Blueprints allow an individual or organization
to start and develop projects with the same basic structure.

Tarbell blueprints are Flask blueprints. From the `Flask documentation <http://flask.pocoo.org/docs/base templates/>`_:

  Flask uses a concept of base templates for making application components and supporting common patterns. base templates can greatly simplify how large applications work, but a base template is not actually an application. Rather it is a base template of how to construct or extend an application.

Tarbell ships with a default, Twitter Bootstrap-based blueprint. It contains boilerplate code with a header, footer, basic analytics and social media support.

Here's a simple ``_blueprint/_blueprint.html`` example.

.. code-block:: django

  <html>
    <head>
      <title>{{ title }}</title>
      {% block css %}
      <link rel="stylesheet" type="text/css" href="css/style.css" />
      {% endblock css %}
    </head>
    <body>
      {% block content %}{% endblock content %}
    </body>
  </html>

To inherit from this template, use Jinja's "extends" syntax in ``index.html`` or other project files you create. All your ``index.html`` needs to contain is:

.. code-block:: django

  {% extends '_base.html' %}

  {% block content %}
  <h1>{{ title }} </h1>
  {{ content|markdown }}
  {% endblock content %}

Notice the ``|markdown`` filter, which is built into Tarbell for convenience. Tarbell Blueprints and projects may define filters, enabled by Jinja2. See :doc:`blueprints` for more

If a blueprint defines a static file or template (e.g. ``_blueprint.css``), it will be available relative to the project's base path (e.g. http://127.0.0.1:5000/style.css). If a project defines a file with the same name, the project's version will be used instead.

See the `open source Tarbell template <https://github.com/newsapps/tarbell-template>`_ for a simple implementation of a Tarbell blueprint.

Template inheritance: Override files from Tarbell blueprints by copying to your project directory
-------------------------------------------------------------------------------------------------

Any file in a Tarbell blueprint can be overridden by a project file.

For example, if your blueprint includes a file ``_blueprint/_nav.html``, you can create a file named ``_nav.html`` in your project directory and it will be published instead of the blueprint version.

This works for static files as well as templates.

Files prefixed with underscores (``_``) will not be generated or published
--------------------------------------------------------------------------

To suppress a file from publishing, use a filename like ``_filename.txt``.

Using context variables
-----------------------

Template data can come from Google spreadsheets, a local or remote CSV or Excel file, or 
tarbell_config.py's ``DEFAULT_CONTEXT``. The context source is configured in ``tarbell_config.py`` 
(see :ref:`tarbell-config` for reference). 

This simple ``DEFAULT_CONTEXT`` shows many of the key template features:

.. code-block:: python

  DEFAULT_CONTEXT = {
      'name': 'nellie-bly',
      'title': 'The Story of Nellie Bly',
      'font_size': '20px',
      # Nested dictionary
      'photos': {
          'intro': {
              'url': 'img/bly01.jpg',
              'caption': 'A caption',
          }
      },
      # Nested list
      'timeline': [
          {'year': '1902', 'description': 'Description...'},
          {'year': '1907', 'description': 'Description...'},
          {'year': '1909', 'description': 'Description...'},
      ],
    }
  }

To print the title in your template, use `{{ title }}`:

.. code-block:: django

  <h1>{{ title }}</h1>

Address a nested dictionary:

.. code-block:: django

  <img src="{{ photos.intro.url }}" alt="{{ photos.intro.caption }}" />
  <aside>{{ photos.intro.caption }}</aside>

Access a list of data:

.. code-block:: django

  <ul>
    {% for year in timeline %}
    <li><strong>{{ year }}</strong>: {{ description }}</li>
    {% endfor %}
  </ul>

Where can context variables be used?
------------------------------------

Context variables can be used in HTML, CSS, and Javascript files. If the text file causes a Jinja
template error (which can happen if the file has Jinja-like markers), the file will be served as static
and the preview server will log an error.

This means that CSS and Javascript files may include variables. ``style.css`` might include:

.. code-block:: css

  #content { font-size: {{ font_size }}; }

Similarly, a Javascript file could include:

.. code-block:: javascript

  var data = {{ photos|tojson }}
  console.log(photos.intro.url);

Use this feature with care! Missing variables could easily break your CSS or Javascript.

Anatomy of a project directory
------------------------------

When you run ``tarbell newproject`` with the default base template, a number of new files and
folders are created, many of them with special significance. Details may vary for other base templates,
but they're likely to have many similar files and concepts.

Here's a rundown of what they all do.

**Files in the root directory:**

index.html
  The first page people will see when they visit your project. This is typically where most of
  the content lives, and is probably where you want to start editing.

tarbell_config.py
  The settings and context for this specific project, described in more detail in the
  `Configuring projects section above <#configuring-projects>`_.


**Files in the _blueprint directory:**

Keep in mind that you rarely want to edit the blueprint files in the ``_blueprint/`` directory - if you want
to change something, copy the file to the root directory and make the change there. If a file of the
same name exists in both the root directory and the ``_blueprint/`` directory, Tarbell will rely on the
one in the root directory.

The only time you should edit the files in the ``_blueprint/`` directory is when 
`you'd like to create or update the blueprint itself <base_templates.html>`_.

_base.html
  The base page template, containing ``<head>`` and ``<body>`` tags, and pointing to many of the Javascript
  and CSS files that will be loaded for each page in the project.

_footer.html
  The partial template containing anything you'd like to appear consistently in the footer at the
  bottom of each page.

_nav.html
  The partial template containing the nav bar that runs along the top of the page.

_spreadsheet.xlsx
  This is the template file that `Google spreadsheets will be based upon
  <google_spreadsheets.html>`_. Unlike most other files in ``_blueprint``, overriding it in your root
  directory won't do anything. However, if you want future projects to be created with a different
  spreadsheet template, you can edit this file and commit it to a repository you control; learn more
  about this feature in the `Developing blueprints <base_templates.html>`_ section.

base.css
  The base CSS file imported by the base template for this project. Override this file in your root
  directory if you'd like to make CSS changes.

blueprint.py
  A Python file that contains a default set of template filters for use in this project. Override
  this file in your root directory if you'd like to alter the behavior of these filters, or add your
  own. If you'd like to make your changes available to other projects, check out the `Developing
  base templates <base_templates.html>`_ section.

favicon.ico
  Favicons are `small logos for websites <http://en.wikipedia.org/wiki/Favicon>`_ that typically
  appear next to a website's name in a browser tab. Change this file in order to change the logo
  associated with your site in users' browser tabs, though keep in mind that favicons have
  `a number of rules <http://www.w3.org/2005/10/howto-favicon>`_ about how they should be
  constructed.

favicon-preview.ico
  This is the icon for the in-development version of a site that appears next to the website's name
  in a browser tab, following the same rules as for favicon.ico above. The key difference is that
  this icon is meant to remind developers and testers that they're not looking at a live site.

index.html
  This is a fallback version of the project's front page, in case the ``index.html`` file in the root
  directory is removed or renamed. It begins life as an exact copy of the root directory's 
  ``index.html``.

Configuring projects
--------------------

Project configuration is kept in the `tarbell_config.py` file in your project's blueprint directory.
See :ref:`tarbell-config` for configuration documentation.

Creating JSON
-------------

You can publish the data coming from your Google spreadsheet as JSON if so desired. To do this, set the `CREATE_JSON`
flag in `tarbell_config.py` to `True`. When you visit `yoursite.com/data.json`, Tarbell will create some JSON
that will look something like this:

.. code-block:: json

  {
    name: "ethelpayne",
    title: "Ethel Payne: A life in journalism",
    headline: "Ethel Payne, Chicago journalist",
    quote: "I stick to my firm, unshakeable belief that the black press is an advocacy press, and that I, as a part of that press, can’t afford the luxury of being unbiased ... when it come to issues that really affect my people, and I plead guilty, because I think that I am an instrument of change.",
    data: [
      {
        name: "Ethel Payne",
        known_for: "civil rights journalism",
        born: "8/14/1911",
        died: 33386
      }
      {
        name: "Grace Hopper",
        known_for: "mathematics and computer programming",
        born: "12/9/1906",
        died: 33604
      },
    ]
  }

The first block of keys and values comes from the `values` workbook. The `data`
array represents another workbook. Any other workbooks you create within your spreadsheet will be represented
as separate arrays.

Optionally, you can use the `CONTEXT_SOURCE_FILE` setting in `tarbell_config.py` to determine your data source,
which can be a URL, local file, CSV or Excel file.

.. note::
  The `data.json` file is created on the fly and will not appear in your project root. You can view and access
  it locally at `127.0.0.1:5000/data.json`.

