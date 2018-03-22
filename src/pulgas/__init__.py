"""
Pulgas -- a Pythonic DSL for configuration formats
"""
from ._impl import config, required, override, optional, custom, sub, load
from ._version import __version__ as _version

__version__ = _version.public()

__all__ = ['config', 'required', 'override', 'optional', 'custom', 'sub',
           'load', '__version__']
