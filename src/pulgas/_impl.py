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


def sub(klass):
    """
    Validate as a pulgas subsection.

    Args:
        klass (type): pulgas configuration to validate as a subsection

    Returns:
        a value of type :code:`klass` as read from the configuration

    Raises:
        schema.SchemaError: invalid configuration data
    """
    return schemalib.Use(klass.validate)


def required(schema, real_name=None):
    """
    A required configuration field.

    Args:
        schema (a type or callable): the specification for this field.
        real_name (str): the name of the configuration field.
            It is optional -- the default is the name of the attribute.
            This is useful especially in cases where the field's name
            is not a valid identifier -- for example, if it contains dashes.
    """
    pulgas_schema = _PulgasSchema(schema=schema, optional=False,
                                  real_name=real_name)
    return attr.attrib(metadata={PULGAS_SCHEMA: pulgas_schema})


def override(schema, default, real_name=None):
    """
    A configuration field that overrides a default value.

    Args:
        schema (a type or callable): the specification for this field.
        default: the default value if the field is not in the configuration.
        real_name (str): the name of the configuration field.
            It is optional -- the default is the name of the attribute.
            This is useful especially in cases where the field's name
            is not a valid identifier -- for example, if it contains dashes.
    """
    pulgas_schema = _PulgasSchema(schema=schema, optional=True,
                                  real_name=real_name)
    return attr.attrib(default=default,
                       metadata={PULGAS_SCHEMA: pulgas_schema})


def optional(schema, real_name=None):
    """
    An optional configuration field.

    In order to access it, first check for its :code:`.has_value`.
    If this is false, this field was absent from the configuration.
    If this is true, the field's value will be in the :code:`.value`
    attribute.

    Args:
        schema (a type or callable): the specification for this field.
        default: the default value if the field is not in the configuration.
        real_name (str): the name of the configuration field.
            It is optional -- the default is the name of the attribute.
            This is useful especially in cases where the field's name
            is not a valid identifier -- for example, if it contains dashes.
    """
    underlying_schema = schemalib.Schema(schema)

    def _to_something(value):
        return _Something(underlying_schema.validate(value))
    schema = schemalib.Use(_to_something)
    pulgas_schema = _PulgasSchema(schema=schema, optional=True,
                                  real_name=real_name)
    return attr.attrib(default=_Nothing(),
                       metadata={PULGAS_SCHEMA: pulgas_schema})


def custom(default=attr.NOTHING):
    """
    Custom configuration field.

    This defines an attribute as a custom configuration field.
    If any of the attributes are :code:`custom`,
    the class must define a class method called
    :code:`__pulgas_from_config__` which takes a dictionary
    and returns a member of the class.

    This allows fine-tuned control over the interpretation
    of the configuration.

    Args:
        default (optional, any type): a default value
    """
    return attr.attrib(default=default)


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
    schema = {schemalib.Optional(name): sub(value)
              for name, value in configuration.collect().items()}
    schema[six.text_type] = object
    return schemalib.Schema(schema).validate(data)
