====================
Create a new project
====================

Create a new project with `tarbell newproject <projectname>`
------------------------------------------------------------

Run:

::

    tarbell newproject mynewproject

You'll be asked a few questions:

::

    This will create a new project in /path/to/current/dir.
    Would you like to continue? [Y/n]

    Available projects:

    [1] Simple page
    [2] Long-form story
    [3] Photo essay
    [4] Searchable map

    Which project would you like to use? [Default: 1] 2

    <<pre-install hooks run here!>>

    Would you like to create a Google spreadsheet for this project? [Y/n]

    <if n>
    Default context data will be copied into config.py

    <if y>
    What Google account should have access to this spreadsheet? [somebody@gmail.com] 

    Generating Google spreadsheet...
    View and edit this spreadsheet at <spreadsheet URL>

    Installing Long-form story template into /path/to/current/dir

    - Copying index.html to /path/to/current/dir/mynewproject/index.html
    ...


    <<post-install hooks run here!>>

    To preview your project, run:

        cd mynewproject
        tarbell serve


