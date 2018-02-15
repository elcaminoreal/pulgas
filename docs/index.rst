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

Example
-------

We can show case how we would parse `flit_`'s configuration.

The top-level of :code:`flit`'s configuration is made up of three
subsections.
We use the :code:`pulgas.sub` to define what is in each subsection.

.. code::

    @pulgas.config()
    class Flit(object):

         metadata = pulgas.required(schema=pulgas.sub(Metadata))
         scripts = pulgas.override(schema=pulgas.sub(Scripts),
                                   default=attr.Factory(Scripts))
         entrypoints = pulgas.override(pulgas.sub(Entrypoints),
                                       default=attr.Factory(Entrypoints))

The simplest subsection is the :code:`Metadata`:

.. code::

    from six import text_type

    @pulgas.config()
    class Metadata(object):

        module = pulgas.required(schema=text_type)
        author = pulgas.required(schema=text_type)
        author_email = pulgas.required(schema=text_type,
                                       real_name='author-email')
        home_page = pulgas.required(schema=text_type, real_name='home-page')

Note that when the real name is not a valid Python name,
we can let pulgas knows what the name is in the configuration file.

        requires = pulgas.override(default=attr.Factory(list),
                                   schema=[str])
        dev_requires = pulgas.override(default=attr.Factory(list),
                                       schema=[str],
                                       real_name='dev-requires')

Note that for the requirements,
we have chosen to use an :code:`override` field --
since the empty list is a good way of saying "no requirements".

        description_file = pulgas.optional(schema=str,
                                           real_name='description-file')

The description file is :code:`optional`.
This means that the user has to test whether it is there.
Example usage might be:

.. code::

    if description_file.has_value:
        with open(description_file.value) as filep:
            description = filep.read()
    else:
            description = ""

Note that we have to explicitly *fetch the value*
from the configuration field.
There are some more fields in the :code:`flit` metadata section,
that we will omit for pedagogical reasons.

The :code:`scripts` section has abitrary keys.
For this, we will define a custom reader:

.. code::

    @pulgas.config()
    class Scripts(object):

        scripts = pulgas.custom(default=attr.Factory(dict))

        @classmethod
        def __pulgas_from_config__(cls, config):
            my_schema = schema.Schema({text_type: text_type})
            validated_config = my_schema.validate(config)
            return cls(scripts=validated_config)

The entrypoints parser is largely similar,
and we will omit it.

.. _flit: http://flit.readthedocs.io/en/latest/pyproject_toml.html#metadata-section

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
