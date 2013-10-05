===============
Build a Project
===============
*Project layout, edit templates and manage Google spreadsheet, tweak CSS, and
take a peek at the Javascript app.*

Now that you've created a new project, let's look at how Tarbell projects are
constructed.

Project layout
==============

A Tarbell template project directory structure looks like this:

    - ``config.py``: Configuration file. Required to detect the project.
    - ``secrets.py``: Set ``GOOGLE_AUTH`` variable to configure authentication. Not tracked by Git.
    - ``templates``: The templates directory contains Jinja templates that will be published at ``/projectname/TEMPLATENAME.html``.
        + ``index.html``: A basic template to start building with.
    - ``static``: The static directory contains static assets like images, CSS, and Javascript. They are published at ``/projectname/FILENAME``.
        + ``js/app.js``: An skeleton Javascript application for your project that is automatically loaded by base template.
        + ``css/style.css``: An empty stylesheet for your project.

What's the difference between static assets and templates?
==========================================================

Static assets are simply served as-is, while templates are provided with
context variables and rendered using Jinja.

Editing templates
=================

Every file that ends in ``.html`` in ``projectname/templates`` will be
published to ``projectname/TEMPLATENAME.html`` and can be previewed at
http://localhost:5000/projectname/TEMPLATENAME.html.

Template basics
---------------

Tarbell uses `Jinja2 <http://jinja.pocoo.org/docs/>`_ for templating and
supports all Jinja2 features.

A basic template looks like:

::

    {% extends '_base.html' %}

    {% block css %}
    {{ super() }} {# Load base styles #}
    <link rel="stylesheet" type="text/css"
        href="{{ static_url('MYPROJECT', '/css/style.css') }}" />
    {% endblock css %}

    {% block content %}
    <h1>{{ title }}</h1>
    <p class="credit">{{ credit }}</p>
    {{ body|process_text }}
    {% endblock content %}

What's ``_base.html``?
======================

The Tarbell template comes with a base template file that sets up some simple
blocks and manages Javascript app loading.

The ``static_url()`` template function
--------------------------------------

The ``static_url(projectname, path)`` function constructs the path to an asset
stored under ``projectname/static`` based on the project's output URL.

Working with Google spreadsheets: The "values" worksheet
--------------------------------------------------------

The **values** worksheet must have "key" and "value" columns. These key-value
pairs will be provided as global variables to templates. So if there's a row
with a key column value of "foo" and a value of "bar", ``{{ foo }}`` in a
template will print ``bar``.

Working with Google spreadsheets: Other worksheets
--------------------------------------------------

Other worksheets can hold freeform data, namespaced by the worksheet name.
Unlike the **values** worksheet, data in these worksheets can be accessed by
iterating through a list or, if a column named "key" is present, by reference
to the value in that column. Some examples with a worksheet named **updates**
should help make this clear.

**A worksheet called "updates"**

====== ================ ==========  ==================================================
key    title            date        url
====== ================ ==========  ==================================================
hadiya Hadiya's friends 05-05-2013  http://graphics.chicagotribune.com/hadiyas-friends
grace  His Saving Grace 02-14-2013  http://graphics.chicagotribune.com/grace
====== ================ ==========  ==================================================

Get worksheet values in template
--------------------------------

The worksheet will be passed to your context as an iterable list, with each
column in the worksheet representing a separate item in the context dictionary.
So in your template, the following code displays the contents of each row in
your spreadsheet:

::

    {% for row in updates %}
    <p> <a href="{{ row.url }}">{{ row.title }}</a> </p> 
    {% endfor %}

Directly accessing a row
------------------------

If there's a header named "key" that contains only unique, simple string values
we can directly access individual rows in that worksheet:

::

    <p> <a href="{{ updates.grace.url }}">{{ updates.grace.title }}</a> </p>

Editing Javascript app
======================

Every project comes with a barebones Javascript app in
``projectname/static/js/app.js``.

The app uses RequireJS and provides Backbone, jQuery, and Underscore libraries
by default.

Wrap your app code in a ``require(['dependency', ...], function(DepObj) { ...
})`` call to include necessary libraries and modules.

::

    // Additional RequireJS configuration
    require.config( {
        paths: {
            moment: '//cdnjs.cloudflare.com/ajax/libs/moment.js/2.0.0/moment.min',
        },
    } );

    // Start our project's app
    require([ 'jquery', 'base/views/NavigationView', 'moment' ],
    function($, NavigationView, moment) {
        console.log("Creating navigation view");
        var nav = new NavigationView({
            el: $('#header'),
            title: { label: 'Tarbell Readme', url: '#top' },
        }).render();

        console.log("Demonstrating momentJS:");
        console.log(new moment());
    });

