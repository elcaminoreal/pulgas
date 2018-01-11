import attr
import schema as schemalib

@attr.s(frozen=True)
class _Marker(object):
    name = attr.ib()

_MISSING = _Marker("MISSING")

PULGAS_SCHEMA = _Marker("PULGAS_SCHEMA")

@classmethod
def _validate(cls, thing):
    from_config = getattr(cls, '__pulgas_from_config__', _MISSING)
    if from_config is not _MISSING:
        return from_config(thing)
    schema = schemalib.Schema({attribute.name:
                               attribute.metadata[PULGAS_SCHEMA]
                               for attribute in cls.__attrs_attrs__})
    processed = schema.validate(thing)
    return cls(**processed)

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

def attrib(schema=None, default=attr.NOTHING):
    if schema is None:
        return attr.attrib(default=default)
    optional = default != attr.NOTHING
    pulgas_schema = PulgasSchema(
    return attr.attrib(default=default, metadata={PULGAS_SCHEMA: schema})

def Use(klass):
    return schemalib.Use(klass.validate)
