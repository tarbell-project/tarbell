Remote configuration
====================

.. note::

    Improving remote use is significant goal for `Tarbell 1.2 <https://github.com/newsapps/flask-tarbell/milestones/1.2>`_.

To run Tarbell on a remote server or to `tarbell publish` via cron on any
server — local or remote — you'll want to generate a credentials file. For remote
use, you'll then need to transfer your Tarbell configuration directory to the
remote server.

Assuming you have Tarbell properly configured, create a credentials file::

    tarbell credentials > ~/.tarbell/credentials.json

Now copy the ``~/.tarbell`` directory to your server. You could use ``scp``, ``rsync``. A preferred
way of doing it is to use a private git repository::

    ssh myuser@myserver.tld
    git clone git@github.com:myuser/tarbell-secrets.git .tarbell

Once the credentials file is in place on the server, you could create a ``fabfile.py`` for deployment
from your server.

.. code-block:: python

    from fabric.api import *

    env.hosts = ['servername']
    env.user = 'myuser'
    env.directory = '/home/myuser/virtualenvs/project'

    @task
    def publish(target='staging'):
        with cd(env.directory):
            with prefix('workon tarbell'):
                run('tarbell publish {0}'.format(target))

Now you can run ``fab publish:production`` and deploy from your server.

Or perhaps a simple cron job, with a line like this in the crontab::

    */15 * * * * myuser /home/myuser/projects/myproject/cron.sh

And a little bash script like this.

.. code-block:: bash

    #!/bin/bash

    workon myproject
    cd /home/myuser/projects/myproject
    tarbell publish production
