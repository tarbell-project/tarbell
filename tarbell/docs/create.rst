===========================
Create and install projects
===========================

Create a new project with `tarbell newproject <projectname>`
------------------------------------------------------------

Run::

    tarbell newproject

You'll be asked a few questions, such as which path you'd like to create the project on, 
whether you want to use Google spreadsheets, and whether you want to instantiate a git repo. 
(See the tutorial for more details.)

When you're done, run a preview server::

    tarbell switch myprojectname

You can now open up `/path/to/myprojectname` and start editing the "index.html"
file.


Install an existing project with `tarbell install <repository-url>`
-------------------------------------------------------------------
The project must include a tarbell_config.py file and be able to be cloned with Git.

Run::

  tarbell install https://urltorepository.com/projectname

e.g.::

  tarbell install https://github.com/sc3/26thandcalifornia.recoveredfactory.net

Structure your project according to common convention
-------------------------------------------------------------------
Web application projects tend to follow pretty well-established patterns, especially in their directory names and structures. Making directories for your stylesheets, data, JavaScript files and images will not only keep you organized but will allow others to easily find what they are looking for.

We recommend you make directories named css, data, js and images in your _base/directory, in keeping with Tribune conventions.






