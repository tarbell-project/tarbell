===============
Install Tarbell
===============

*Clone repository, install virtual environment, install requirements, configure
your system for Amazon S3, and run a test server.*

Tarbell is a Python library based on Flask which powers static sites. Truth be
told, it doesn't do much on its own except read a directory and render
templates in any subdirectory it finds a ``config.py`` file. To see Tarbell in
action, you should probably start with the Tarbell template, which sets up an
Amazon S3 publishing workflow and basic framework for building modern web apps
using Tarbell.

Make sure you have ``python`` (2.6+), ``git``, ``pip``, ``virtualenv`` and
``virtualenv-wrapper`` installed on your system.

::

    git clone https://github.com/newsapps/tarbell
    cd tarbell
    mkvirtualenv tarbell
    pip install -r requirements.txt
    python runserver.py

Now visit http://localhost:5000/readme in your browser. You should see the
latest version of this page.

How do I install these tools on my system?
==========================================

For a very basic guide, see the `Chicago Birthrates installation docs.
<https://hackpad.com/Install-Chicago-Birthrates-6V2O2Un04Ow>`_

For more detailed, Mac-specific information, see Brian Boyer's `Lion dev
environment notes. <https://gist.github.com/brianboyer/1696819>`_
