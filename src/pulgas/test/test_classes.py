"""
Tests for the pulgas configuration specification DSL.
"""

import unittest

import attr
import schema
import toml

import pulgas

# The following configuration formats are included here
# to showcase the API for specifying configuration formats --
# their semantics are irrelevant.
#
# For real uses, the master definition should be in the format here,
# and in that case, docstrings can serve as a way of documenting
# the format's semantics.


# pylint: disable=missing-docstring
@pulgas.config()
class Pipfile(object):

    @pulgas.config()
    class Source(object):

        url = pulgas.attrib(schema=str)
        verify_ssl = pulgas.attrib(schema=schema.Optional(bool))
        name = pulgas.attrib(schema=str)

    # Copied from PEP 508, removed "extra"
    @pulgas.config()
    class Requires(object):

        _optional_str = pulgas.attrib(schema=str, optional=True)
        os_name = sys_platform = platform_machine = _optional_str
        platform_python_implementation = sys_platform = _optional_str
        platform_machine = platform_python_implementation = _optional_str
        platform_release = platform_system = platform_version = _optional_str
        python_version = python_full_version = _optional_str
        implementation_name = implementation_version = _optional_str
        del _optional_str

    @pulgas.config()
    class Packages(object):

        packages = pulgas.attrib(default=attr.Factory(dict))

        @classmethod
        def __pulgas_from_config__(cls, config):
            spec = schema.Or(str,  # Should be version str
                             pulgas.Use(Pipfile.PackageSpec))
            my_schema = schema.Schema({str: spec})
            validated_config = my_schema.validate(config)

            def to_spec(value):
                if isinstance(value, str):
                    return Pipfile.PackageSpec(version=value)
                return value
            packages = {name: to_spec(value)
                        for name, value in validated_config.items()}
            return cls(packages=packages)

    @pulgas.config()
    class PackageSpec(object):

        extras = pulgas.attrib(schema=[str], default=attr.Factory(list))
        _optional_str = pulgas.attrib(schema=str, optional=True)
        git = ref = file = path = index = os_name = markers = _optional_str
        del _optional_str
        editable = pulgas.attrib(schema=bool, default=False)
        version = pulgas.attrib(schema=str, default='*')

    source = pulgas.attrib(schema=[pulgas.Use(Source)],
                           default=[Source(url=('https://pypi.python.org/'
                                                'simple'),
                                           verify_ssl=True,
                                           name='pypi')])

    requires = pulgas.attrib(pulgas=Requires, optional=True)

    packages = pulgas.attrib(pulgas=Packages, optional=True)

    dev_packages = pulgas.attrib(pulgas=Packages,
                                 real_name='dev-packages',
                                 optional=True)


@pulgas.config()
class PyProject(object):

    @pulgas.config()
    class BuildSystem(object):

        requires = pulgas.attrib(schema=[str], default=attr.Factory(list))
        build_backend = pulgas.attrib(schema=str, real_name='build-backend',
                                      optional=True)

    build_system = pulgas.attrib(pulgas=BuildSystem, real_name='build-system')

    tool = pulgas.attrib(schema=object, default=attr.Factory(dict))
# pylint: enable=missing-docstring


def _parse_inline_doc_toml(content):
    lines = content.splitlines()[1:]
    initial_whitespace = len(lines[0]) - len(lines[0].lstrip())
    stripped = [line[initial_whitespace:] for line in lines]
    real_content = '\n'.join(stripped) + '\n'
    parsed = toml.loads(real_content)
    return parsed


class ClassTest(unittest.TestCase):

    """
    Test the pulgas specification classes.
    """

    def test_simple_pipfile(self):
        """
        Parsing a Pipfile validates and converts to Pipfile instance.
        """
        content = """
        [[source]]
        url = 'https://pypi.python.org/simple'
        verify_ssl = true
        name = 'pypi'

        [requires]
        python_version = '2.7'

        [packages]
        requests = { extras = ['socks'] }
        records = '>0.5.0'
        django = { git = 'https://github.com/django/django.git', ref = '1.11.4', editable = true }
        "e682b37" = {file = "https://github.com/divio/django-cms/archive/release/3.4.x.zip"}
        "e1839a8" = {path = ".", editable = true}
        pywinusb = { version = "*", os_name = "=='nt'", index="pypi"}

        [dev-packages]
        nose = '*'
        unittest2 = {version="<3.0", markers="python_version<'2.7.9'"}
        """
        res = Pipfile.validate(_parse_inline_doc_toml(content))
        dct = attr.asdict(res, recurse=False)
        source = dct.pop('source')
        first_one = source.pop(0)
        self.assertEquals(source, [])
        self.assertIsInstance(first_one, Pipfile.Source)
        parts = attr.asdict(first_one)
        self.assertEquals(parts.pop('url'), 'https://pypi.python.org/simple')
        self.assertEquals(parts.pop('verify_ssl'), True)
        self.assertEquals(parts.pop('name'), 'pypi')
        self.assertEquals(parts, {})
        requires = dct.pop('requires')
        self.assertTrue(requires.has_value)
        parts = attr.asdict(requires.value, recurse=False)
        python_version = parts.pop('python_version')
        self.assertTrue(python_version.has_value)
        self.assertEquals(python_version.value, '2.7')
        for key, value in parts.items():
            self.assertEquals((key, value.has_value), (key, False))
        dev_packages = dct.pop('dev_packages')
        self.assertTrue(dev_packages.has_value)
        dev_packages = dev_packages.value.packages
        nose = dev_packages.pop('nose')
        self.assertEquals(nose.version, '*')
        self.assertFalse(nose.git.has_value)
        self.assertFalse(nose.markers.has_value)
        unittest2 = dev_packages.pop('unittest2')
        self.assertTrue(unittest2.markers.has_value)
        self.assertNotEqual(unittest2.version, '*')
        self.assertEquals(dev_packages, {})
        packages = dct.pop('packages')
        self.assertTrue(packages.has_value)
        self.assertIsInstance(packages.value, Pipfile.Packages)
        packages = packages.value.packages
        self.assertEquals(packages.pop('requests').version, '*')
        self.assertEquals(dct, {})

    def test_simple_pyproject(self):
        """
        Parsing a pyproject.toml validates and converts to PyProject instance
        """
        content = """
        [build-system]
        requires = ["flit"]
        build-backend = "flit.buildapi"

        [tool.flit.metadata]
        module = "foobar"
        author = "Sir Robin"
        author-email = "robin@camelot.uk"
        home-page = "https://github.com/sirrobin/foobar"
        """
        parsed = _parse_inline_doc_toml(content)
        res = PyProject.validate(parsed)
        things = attr.asdict(res, recurse=False)
        # We ignore things under "tool"
        things.pop('tool')
        build_system = things.pop('build_system')
        self.assertEquals(things, {})
        self.assertIsInstance(build_system, PyProject.BuildSystem)
        things = attr.asdict(build_system, recurse=False)
        self.assertEquals(things.pop('requires'), ['flit'])
        build_backend = things.pop('build_backend')
        self.assertEquals(things, {})
        self.assertTrue(build_backend.has_value)
        build_backend_value = build_backend.value
        self.assertEquals(build_backend_value, 'flit.buildapi')
