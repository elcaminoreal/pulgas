"""
Pulgas -- a Pythonic DSL for configuration formats
"""
from ._impl import config, attrib, Use
from ._version import __version__ as _version

__version__ = _version.public()

__all__ = ['config', 'attrib', 'Use', '__version__']
