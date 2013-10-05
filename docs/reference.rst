=========
Reference
=========
*Configure Tarbell, set up a Flask Blueprint, special base project.*

Configuring Tarbell
-------------------

When your project was created, a ``config.py`` file was created in the project
directory, which lets Tarbell find your project. This file can be empty, but
also accepts several configuration options:

    - ``GOOGLE_DOC``: A dict of Google docs parameters to access a spreadsheet.

    Takes ``key``, ``account``, and ``password`` parameters.

    The default template stores account and password variables in a file called
    ``secrets.py`` in variable called ``GOOGLE_AUTH``. **Use secrets.py to keep
    your authentication information out of version control.**

    ::

        GOOGLE_DOC = {
            'key': "BIGLONGSTRINGOFLETTERSANDNUMBERS",
            'account': "some+account@gmail.com",
            'password': "++GmailPassWord++",
        }

    - ``DEFAULT_CONTEXT``: Default context variables to make available to all project templates.

    ::

        DEFAULT_CONTEXT = {
            'ad_path': '',
            'analytics_path': '',
        }

    - ``DONT_PUBLISH``: If ``True``, this project will not be published to S3.

    ::

        DONT_PUBLISH=True

    Default: ``False``

    - ``URL_ROOT``: Override the published URL to differ from the directory
      name.

    ::

        URL_ROOT='totally-awesome-project'

    Default: ``None`` (publish using name of directory)

    - ``CREATE_JSON``: If ``False``, do not publish JSON data. Useful if
      spreadsheets contain secrets or sensitive information, and so should not
      be public.

    ::

        CREATE_JSON = False

    Default: ``True``

For advanced uses, you can turn your project into a Flask Blueprint in order to
register template filters or dynamically set the template context.

::

    from flask import Blueprint
    blueprint = Blueprint('awesome_project', __name__)

    # Register template filter
    @blueprint.app_template_filter('my_filter')
    def my_filter(text):
       return text.strip()

    @blueprint.app_context_processor
    def context_processor():
        """
        Add "my_variable" to context
        """
        context = {
            'my_variable': 'My variable would be more awesome in real life, like reading a file or API data.",
        }

        return context

Now you can reference ``{{ my_variable }}`` in your templates, or call your
filter on a template variable ``{{ my_variable|my_filter }}``.

Base project
------------

If any project contains a ``URL_ROOT = ''`` configuration, that project will:

    - Be available at the root URL (``/index.html``, ``/css/style.css``, etc).
    - Always be published when deploying.

JSON publishing
---------------

By default, every project's Google spreadsheet will be baked out to a JSON file
representing each worksheet. For example, most projects will have a
``myproject/json/values.json`` that represents the contents of the "values"
worksheet.

This means you can build pure Javascript apps using Tarbell in the framework of
your choice. Just AJAX load or bootstrap the JSON data.

To disable this behavior, add a line to your ``config.py``:

::

    CREATE_JSON = False

If you disable this behavior and need data available to Javascript
applications, simply bootstrap the dataset provided it isn't too big. Here's
something you might put in ``myproject/index.html``:

::

    {% block scripts %}
    <script type="text/javascript">
        // Convert whole worksheet to JSON
        var authors = {{ authors|tojson }}

        // Filter a worksheet
        var locations = [ {% for address in locations %}
            { state: '{{ address.state }}' },
        {% endfor %} ];

        // Now process or display 'authors' and 'locations' ...
    </script>
    {% endblock %}
