======================
Command line reference
======================

``tarbell configure``
---------------------

**Usage:** ``tarbell configure <optional: subcommand>``

Subcommands: ``drive``, ``s3``, ``path``, ``templates``

Configures Tarbell. Specifying a subcommand will set up just that section of the configuration.

``tarbell newproject``
----------------------

**Usage:** ``tarbell newproject <optional: projectname>``

Create a new Tarbell project.


``tarbell serve``
-----------------

*Requires current directory to be a Tarbell project.*

**Usage:** ``tarbell serve <optional: ip:port>``

Run a preview server. Specify an optional listening address, such as "0.0.0.0" or "192.143.23.10:5000".

``tarbell publish``
-------------------

*Requires current directory to be a Tarbell project.*

**Usage:** ``tarbell publish <optional: target, default: staging>``

Publish a Tarbell project to Amazon S3 using optional target (configured in ``tarbell_config.py``).

``tarbell update``
------------------

*Requires current directory to be a Tarbell project.*

**Usage:** ``tarbell update``

Updates blueprint with git submodule update.

``tarbell generate``
--------------------

*Requires current directory to be a Tarbell project.*

**Usage:** ``tarbell generate <optional: output directory>``

Make HTML on the file system. If output directory is not specified, a temporary directory will be
used.

``tarbell switch``
------------------

**Usage:** ``tarbell switch <project name>``

Serve the project specified by project name if it exists in your default Tarbell project directory.

``tarbell list``
----------------

**Usage:** ``tarbell list``

List projects from your default Tarbell project directory.

``tarbell install``
-------------------

**Usage:** ``tarbell install <git repository url>``

Install a Tarbell project from the Git repository url specified.

``tarbell install-template``
----------------------------

**Usage:** ``tarbell install-template <git repository url>``

Install a base template from the given repository url.

``tarbell token``
-----------------

**Usage:** ``tarbell token``

Print JSON with the current OAuth token.
