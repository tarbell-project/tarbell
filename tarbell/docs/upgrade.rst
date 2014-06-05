=========
Upgrading
=========

Upgrade an existing Tarbell installation
----------------------------------------

If you've already installed Tarbell, you can upgrade with:

..code-block:: bash

  pip install -U tarbell

.. note::

  In version 0.9-beta6, some naming conventions changed. The ``_base`` folder and ``base.py`` file are
  now called ``_blueprint`` and ``blueprint.py``. Future versions in the 0.9.x and 1.0.x branches will
  maintain backwards compatibility with Tarbell projects created using the old naming convention.
