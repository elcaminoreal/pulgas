.. Copyright (c) Moshe Zadka
   See LICENSE for details.

Pulgas
======

.. toctree::
   :maxdepth: 2

Overview
--------

Pulgas is a plugin-based configuration specification library.
It can be used to read a low-level configuration format,
such as TOML (or JSON/HJSON or YAML),
validate it against each plugin,
and return the validated values.

Pulgas uses the :code:`gather` library in order to find plugins.
In order to avoid globals, pulgas does *not* define a specific collector:
that is left up to the pulgas user.

Definining a collector is easy:

.. code:

    CONFIGURATION = pulgas.Collector()

The plugin configuration validator is a class:

.. code::

    @CONFIGURATION.register(name="<NAME>")
    @pulgas.config()
    class SomeClass(object):

        configuration_field = pulgas.



API
---
.. automodule:: pulgas
   :members: config, required, override, optional, custom, Use, load
