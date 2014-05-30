Using Google spreadsheets
=========================

The `values` worksheet
----------------------

The values worksheet must have "key" and "value" columns. These key-value pairs will be provided as global variables to templates. So if there's a row with a key column value of "foo" and a value of "bar", `{{ foo }}` in a template will print bar.

Take this sample worksheet:

=====  =============
key    value
=====  =============
title  Project title
intro  Project intro
=====  =============

A `values` worksheet that contains this data provides the `{{ title }}` and `{{ intro }}` variables to the template.

Use them in your templates:

.. code-block:: html

    <h2>{{ title }}</h2>
    <p class="intro">{{ intro }}</p>


Named worksheets
----------------

Other worksheets can hold any kind of data supported by Google spreadsheets. These variables can be accessed by their worksheet name.

If there is no `key` column in the worksheet, the worksheet can be accessed as a list. Imagine a spreadsheet named `cars` with these values:

=======  ====
model    mpg
=======  ====
Civic    25.9
Accord   28.1
Element  24.6
=======  ====

You can access these variables in your spreadsheet with a loop:

.. code-block:: django

    {% for car in cars %}
      <h3>{{ car.model }}</h3>
      <p>MPG: {{ car.mpg }}</p>
    {% endfor %}


If a column named `key` does exist, elements may be accessed by key. Imagine a spreadsheet named `companies` with these values:

=====  ======  =======
key    name    country
=====  ======  =======
ford   Ford    U.S.A.
honda  Honda   Japan
volvo  Volvo   Sweden
=====  ======  =======

You can access these variables by their key name:

.. code-block:: django

    <p>{% manufacturers.ford.name %} is from {% manufacturers.ford.country %}</p>


Worksheet, column, and key names are slugified
----------------------------------------------

Spaces and dashes are replaced with underscores (`_`). Non alphanumeric characters are removed. Case is preserved.

Examples of names that will be transformed:

- `My Worksheet` becomes `My_Worksheet`
- `My key\\n` becomes `My_key`
- `my-Column` becomes `my_Column`

Names that will not be transformed:

- `MyColumn` remains `MyColumn`
- `mycolumn` remains `mycolumn`
- `my_column` remains `my_column`


Worksheets, columns, and keys names preceded by `_` (underscore) are ignored
----------------------------------------------------------------------------

Precede any worksheet name, column name, or key with an underscore to hide it from 
your templates and JSON data.
