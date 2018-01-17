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

        required_field = pulgas.required(schema=int)
        field_with_default = pulgas.required(schema=float, default=0.0)
        optional_field = pulgas.optional(schema=bool)

If further structure is needed,
inner classes can be defined:

.. code::

    @CONFIGURATION.register(name="<NAME>")
    @pulgas.config()
    class SomeClass(object):

        @pulgas.config()
        class FirstPart(object):

            field_one = pulgas.required(schema=int)

        top_level = pulgas.required(schema=int)
        inner_config = pulgas.required(schema=pulgas.Use(FirstPart)
    

API
---
.. automodule:: pulgas
   :members: config, required, override, optional, custom, Use, load
