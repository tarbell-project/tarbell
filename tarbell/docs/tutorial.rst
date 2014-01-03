================
Tutorial
================

Let's build a website about celebrated Chicago journalist Ethel Payne! 

First you need Tarbell. Fair warning, you're going to have to run these commands in
a terminal::

    pip install tarbell==0.9b4

Got it? Now configure Tarbell::

    tarbell configure

For our tutorial, just say "no" to configuring Google or Amazon. It's optional!

Now that you've got Tarbell configured, create a new project::

  tarbell newproject

You'll need to answer a few questions::

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

  - Cloning https://github.com/newsapps/tarbell-template to /Users/davideads/tarbell/ethelpayne

  Copying configuration file
  Copying _base/_spreadsheet.xlsx to tarbell.py's DEFAULT_CONTEXT

  - Creating tarbell.py project configuration file

  - Done copying configuration file

  Setting up git remote repositories

  - Renaming master to update_project_template

  - Add and commit tarbell.py

  What is the URL of your project repository? (e.g. git@github.com:eads/myproject.git, leave blank to skip) 

  - Not setting up remote repository. Use your own version control!

  All done! To preview your new project, type:

  tarbell switch ethelpayne

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

You're ready to start editing your template.

First, set some project data in `/path/to/project` (in this case `/Users/davideads/tarbell/ethelpayne/tarbell.py`). 
Open the file in your favorite editor. It should look like this::

  # -*- coding: utf-8 -*-

  """
  Tarbell project configuration
  """

  # Short project name
  NAME = "ethelpayne"

  # Descriptive title of project
  TITLE = "Ethel Payne: A life in journalism"

  # Google spreadsheet key
  #SPREADSHEET_KEY = "None"

  # S3 bucket configuration
  S3_BUCKETS = {
      # Provide target -> s3 url pairs, such as:
      # "mytarget": "s3://mys3url.bucket.url/some/path"
      "staging": "apps.beta.chicagotribune.com/someproject",
      "production": "apps.chicagotribune.com/someproject/",
  }

  # Repository this project is based on (used for updates)
  TEMPLATE_REPO_URL = "https://github.com/newsapps/tarbell-template"

  # Default context variables
  DEFAULT_CONTEXT = {
      'data': [   {   'born': 2535.0,
                      'died': 33604.0,
                      'name': u'Grace Hopper'},
                  {   'born': 4244.0,
                      'died': 33386.0,
                      'name': u'Ethel Payne'}],
      'headline': u'Ida Tarbell quote',
      'intro': u'Rockefeller and his associates did not build the Standard Oil Co. in the board rooms of Wall Street banks. They fought their way to control by rebate and drawback, bribe and blackmail, espionage and price cutting, by ruthless ... efficiency of organization.',
      'name': 'dontkillmy',
      'quote': u"To know every detail of the oil trade, to be able to reach at any moment its remotest point, to control even its weakest factor \u2014 this was John D. Rockefeller's ideal of doing business. It seemed to be an intellectual necessity for him to be able to direct the course of any particular gallon of oil from the moment it gushed from the earth until it went into the lamp of a housewife. \n\nThere must be nothing \u2014 nothing in his great machine he did not know to be working right. It was to complete this ideal, to satisfy this necessity, that he undertook, late in the seventies, to organise the oil markets of the world, as he had already organised oil refining and oil transporting.",
      'quote_author': u'Ida Tarbell, History of the Standard Oil Company',
      'title': u'Ethel Payne: A life in journalism'
  }

Edit the last section to include a new variable::

  DEFAULT_CONTEXT = {
      # ...
      'title': u'Ethel Payne: A life in journalism',
      'payne_quote': u'I stick to my firm, unshakeable belief that the black press is an advocacy press, and that I, as a part of that press, can’t afford the luxury of being unbiased ... when it come to issues that really affect my people, and I plead guilty, because I think that I am an instrument of change.',
      'payne_quote_author': u'Ethel Payne',
  }

Now edit your project's `index.html`. ::

  {% extends "_base.html" %}

  {% block content %}

  {% if PREVIEW_SERVER %}
  <div class="alert alert-warning">
    <p>Edit this <a href="https://docs.google.com/spreadsheet/ccc?key={{ SPREADSHEET_KEY }}" target="_blank">project's Google spreadsheet</a>.</p> 

    <p>You can modify this file by editing <code>{{ PROJECT_PATH }}/index.html</code>.</p>

    <p>This block will not publish when <code>tarbell publish</code> is invoked.</p>
  </div>
  {% endif %}

  <div class="jumbotron">
    <h1>{{ headline }}</h1>
    <p>{{ intro }}</p>
  </div>

  <div class="row">
    <div class="col-md-8">
      <blockquote>
        {{ quote|markdown }}
        <small>{{ quote_author }}</small>
      </blockquote>
    </div>

    <div class="col-md-4">
      <table class="table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Born</th>
            <th>Died</th>
          </tr>
        </thead>
        <tbody>
        {% for row in data %}
        <tr>
          <td>{{ row.name }}</td>
          <td>{{ row.born|format_date }}</td>
          <td>{{ row.died|format_date }}</td>
        </tr>
        {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
  {% endblock content %}


Change the quote section to use your new variables. Change this::

    <div class="col-md-8">
      <blockquote>
        {{ quote|markdown }}
        <small>{{ quote_author }}</small>
      </blockquote>
    </div>

to this::

    <div class="col-md-8">
      <blockquote>
        {{ payne_quote|markdown }}
        <small>{{ payne_quote_author }}</small>
      </blockquote>
    </div>

Reload the server at http://127.0.0.1:5000 in your web browser to see your changes!
