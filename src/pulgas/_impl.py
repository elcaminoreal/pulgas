"""
Implementation code for the pulgas DSL
"""
import attr
import schema as schemalib
import six


@attr.s(frozen=True)
class _Marker(object):
    name = attr.ib()


_MISSING = _Marker("MISSING")

PULGAS_SCHEMA = _Marker("PULGAS_SCHEMA")


def _get_schema_key(attribute):
    return attribute.metadata[PULGAS_SCHEMA].get_schema_key(attribute.name)


@attr.s(frozen=True)
class _Nothing(object):

    has_value = False


@attr.s(frozen=True)
class _Something(object):

    has_value = True

    value = attr.ib()


@classmethod
def _validate(cls, thing):
    from_config = getattr(cls, '__pulgas_from_config__', _MISSING)
    if from_config is not _MISSING:
        return from_config(thing)
    config_name_to_name = {attribute.metadata[PULGAS_SCHEMA].real_name or
                           attribute.name:
                           attribute.name
                           for attribute in cls.__attrs_attrs__}
    schema = schemalib.Schema({_get_schema_key(attribute):
                               attribute.metadata[PULGAS_SCHEMA].schema
                               for attribute in cls.__attrs_attrs__})
    processed = schema.validate(thing)
    processed_named = {config_name_to_name[name]: value
                       for name, value in processed.items()}
    return cls(**processed_named)


def config():
    """
    Mark a class as a pulgas DSL configuration specification
    """
    def _decorate(klass):
        klass = attr.attrs(klass)
        klass.validate = _validate
        return klass
    return _decorate


@attr.s(frozen=True)
class _PulgasSchema(object):

    schema = attr.ib()
    optional = attr.ib()
    real_name = attr.ib()

    def get_schema_key(self, name):
        """
        Calculate the key in a dictionary schema.

        Args:
            name (str): the field name

        Returns:
            Something suitable as a key in a dictionary passed to
            :code:`Schema`. Accounts for optionality and for name-override.
        """
        if self.real_name is not None:
            name = self.real_name
        if not self.optional:
            return name
        return schemalib.Optional(name)


# pylint: disable=invalid-name
def Use(klass):
    """
    Validate using a pulgas configuration specifier.
    """
    return schemalib.Use(klass.validate)
# pylint: enable=invalid-name


def attrib(schema=None, optional=False, default=attr.NOTHING,
           pulgas=None, real_name=None):
    """
    Configuration field.

    Args:
        schema (a type or callable): the specification for this node
        optional (bool): whether this is optional
        default: default value. Note that optional attributes cannot
            have defaults
        pulgas (a pulgas class): specification for node format
            (in this case schema and default arguments ae ignored)
        real_name (str): instead of using the attribute's name as the
            name to locate this name by, use an explcit one.
            Useful when configuration field name is not a valid Python
            name (usually because of hyphens).
    Returns:
        A marker used by the :code:`config` class decorator to know
        this attribute corresponds to a configuration field.
    """
    if optional:
        default = _Nothing()
    if pulgas is not None:
        schema = Use(pulgas)
    if schema is None:
        return attr.attrib(default=default)
    if default == _Nothing():
        underlying_schema = schemalib.Schema(schema)

        def _to_something(value):
            return _Something(underlying_schema.validate(value))
        schema = schemalib.Use(_to_something)
    optional = (default != attr.NOTHING)
    pulgas_schema = _PulgasSchema(schema=schema, optional=optional,
                                  real_name=real_name)
    return attr.attrib(default=default,
                       metadata={PULGAS_SCHEMA: pulgas_schema})


def load(configuration, data):
    """
    Load validated configuration

    Args:
        configuration (gather.Collector): a collector of configurations
        data (dict): data read from a configuration file

    Returns:
        dictionary mapping configuration names to validated configuration
        objects

    Raises:
        schema.SchemaError: invalid configuration data
    """
    schema = {schemalib.Optional(name): Use(value)
              for name, value in configuration.collect().items()}
    schema[six.text_type] = object
    return schemalib.Schema(schema).validate(data)
