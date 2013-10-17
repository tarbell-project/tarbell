===========================
Create or install a project
===========================

Create a new project with `tarbell newproject <projectname>`
------------------------------------------------------------

Run::

    tarbell newproject mynewproject

You'll be asked a few questions::

  Creating nellie-bly

  Where would you like to create this project? [/Users/davideads/tarbell/nellie-bly] 

  What is the project's full title? (e.g. My awesome project) The Story of Nellie Bly

  Pick a template

    [1] Basic Bootstrap 3 template
        https://github.com/newsapps/tarbell-template

    [2] Searchable map template   
        https://github.com/eads/tarbell-map-template


  Which template would you like to use? [1] 1

  - Cloning https://github.com/newsapps/tarbell-template to /Users/davideads/tarbell/nellie-bly

  Copying configuration file
  Copying _base/_spreadsheet.xlsx to tarbell.py's DEFAULT_CONTEXT

  - Creating tarbell.py project configuration file

  - Done copying configuration file

  Setting up git remote repositories

  - Renaming master to update_project_template

  - Add and commit tarbell.py

  What is the URL of your project repository? (e.g. git@github.com:eads/myproject.git, leave blank to skip) git@github.com:eads/nellie-bly.git

  Creating new remote 'origin' to track git@github.com:eads/nellie-bly.git.

  Warning: Don't forget! It's up to you to create this remote and push to it.

  All done! To preview your new project, type:

  tarbell switch nellie-bly

  You got this!


You can now open up ` /Users/davideads/tarbell/nellie-bly` and start editing the "index.html"
file.


Install an existing project with `tarbell install <repository-url>`
-------------------------------------------------------------------

The project must include a `tarbell.py` file and be able to be cloned with Git.
