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
        field_with_default = pulgas.override(schema=float, default=0.0)
        optional_field = pulgas.optional(schema=bool)

Fields
------

Fields come in three kinds, shown above.
The first kind, :code:`required` fields,
are the simplest.
If they are not present,
the configuration is invalid.
The second type, :code:`override` fields,
have a default.
If they are present,
the value will override the default.
Note that the default is not validated,
nor converted.

Finally, there are optional fields.
Optional fields cannot be accessed directly.
After validation,
they will support the :code:`has_value`
attribute.
If it is false,
that means they were not present in the configuration.

If :code:`has_value` is true,
the :code:`value` attribute will point to the value
specified in the configuration.
Otherwise, :code:`value` will *not exist* --
accessing it will cause an :code:`AttributeError` to be raised.

Subsections
-----------

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
        inner_config = pulgas.required(schema=pulgas.sub(FirstPart))

The :code:`sub` function
(for "subsection")
defines a subsection of the configuration that should comply with
a different class.
Inner classes are ideal for that,
since they will seldom be instantiated explicitly.

Custom parsing
--------------

The final field type is :code:`custom`.
Note that that field type comes without semantics --
not even specifying what in the configuration it will read.
If any fields are :code:`custom`,
the configuration class must define a class method
:code:`__pulgas_from_config__`,
which will be called with the appropriate section of the configuration
(all of it or a subsection, depending on where the class is encountered).
It must return an appropriate configuration object,
or raise a :code:`schema.SchemaError` is validation has failed.

Note that if
:code:`__pulgas_from_config__` is defined,
even if no fields are :code:`custom`,
it will still be called to create and validate the configuration.

API
---
.. automodule:: pulgas
   :members: config, required, override, optional, custom, sub, load
