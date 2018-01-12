import attr
import schema as schemalib

@attr.s(frozen=True)
class _Marker(object):
    name = attr.ib()

_MISSING = _Marker("MISSING")

PULGAS_SCHEMA = _Marker("PULGAS_SCHEMA")

def _get_schema_key(attribute):
    return attribute.metadata[PULGAS_SCHEMA].get_schema_key(attribute.name)

@classmethod
def _validate(cls, thing):
    from_config = getattr(cls, '__pulgas_from_config__', _MISSING)
    if from_config is not _MISSING:
        return from_config(thing)
    config_name_to_name = {attribute.metadata[PULGAS_SCHEMA].real_name or attribute.name:
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
    def _decorate(klass):
        klass = attr.attrs(klass)
        klass.validate = _validate
        return klass
    return _decorate

@attr.s(frozen=True)
class PulgasSchema(object):

    schema = attr.ib()
    optional = attr.ib()
    real_name = attr.ib()

    def get_schema_key(self, name):
        if self.real_name is not None:
            name = self.real_name
        if self.optional:
            return schemalib.Optional(name)
        else:
            return name

def Use(klass):
    return schemalib.Use(klass.validate)

def attrib(schema=None, default=attr.NOTHING, pulgas=None, real_name=None):
    if pulgas is not None:
        schema = Use(pulgas)
        default = pulgas()
    if schema is None:
        return attr.attrib(default=default)
    optional = (default != attr.NOTHING)
    pulgas_schema = PulgasSchema(schema=schema, optional=optional,
                                 real_name=real_name)
    return attr.attrib(default=default,
                        metadata={PULGAS_SCHEMA: pulgas_schema})
