Make a virtual environment

`mkvirtualenv tarbell`

Install tarbell in editable mode:

`pip install --editable .`

To run the local admin site:

`tarbell admin`

And then visit http://127.0.0.1:5001 in your browser.

If you have never configured tarbell before, you should see the configuration modal, which will walk you through the configuration steps.  

Otherwise, you will just see the main page with the Projects, Blueprints, and Settings tabs.

To "reset" the state of your tarbell installation, delete `~/.tarbell` and reload the local admin site.

To force the configuration modal to appear, visit http://127.0.0.1:5001?configure in your browser.



