import unittest

import attr
import schema
import toml

import pulgas

@pulgas.config()
class Pipfile(object):

    @pulgas.config()
    class Source(object):

        url = pulgas.attrib(schema=str)
        verify_ssl = pulgas.attrib(schema=schema.Optional(bool))
        name = pulgas.attrib(schema=str)

    ## Copied from PEP 508, removed "extra"
    @pulgas.config()
    class Requires(object):

        os_name = pulgas.attrib(schema=str, optional=True)
        sys_platform = pulgas.attrib(schema=str, optional=True)
        platform_machine = pulgas.attrib(schema=str, optional=True)
        platform_python_implementation = pulgas.attrib(schema=str, optional=True)
        platform_release = pulgas.attrib(schema=str, optional=True)
        platform_system = pulgas.attrib(schema=str, optional=True)
        platform_version = pulgas.attrib(schema=str, optional=True)
        python_version = pulgas.attrib(schema=str, optional=True)
        python_full_version = pulgas.attrib(schema=str, optional=True)
        implementation_name = pulgas.attrib(schema=str, optional=True)
        implementation_version = pulgas.attrib(schema=str, optional=True)

    @pulgas.config()
    class Packages(object):

        packages = pulgas.attrib(default=attr.Factory(dict))

        @classmethod
        def __pulgas_from_config__(cls, config):
            my_schema = schema.Schema({str:
                                       schema.Or(str, # Should be version str
                                                 pulgas.Use(Pipfile.PackageSpec))})
            validated_config = my_schema.validate(config)
            packages = {name: Pipfile.PackageSpec(version=value)
                              if isinstance(value, str)
                              else value
                              for name, value in validated_config.items()}
            return cls(packages=packages)

    @pulgas.config()
    class PackageSpec(object):

        extras = pulgas.attrib(schema=[str], default=attr.Factory(list))
        git = pulgas.attrib(schema=str, optional=True)
        ref = pulgas.attrib(schema=str, optional=True)
        editable = pulgas.attrib(schema=bool, default=False)
        file = pulgas.attrib(schema=str, optional=True)
        path = pulgas.attrib(schema=str, optional=True)
        version = pulgas.attrib(schema=str, default='*')
        index = pulgas.attrib(schema=str, optional=True)
        os_name = pulgas.attrib(schema=str, optional=True)
        markers = pulgas.attrib(schema=str, optional=True)


    source = pulgas.attrib(schema=[pulgas.Use(Source)],
                           default=[Source(url='https://pypi.python.org/simple',
                                          verify_ssl=True,
                                          name='pypi')])

    requires = pulgas.attrib(pulgas=Requires, optional=True)

    packages = pulgas.attrib(pulgas=Packages, optional=True)

    dev_packages = pulgas.attrib(pulgas=Packages, real_name='dev-packages', optional=True)

class ClassTest(unittest.TestCase):

    def test_simple_pipfile(self):
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
        unittest2 = {version = ">=1.0,<3.0", markers="python_version < '2.7.9' or (python_version >= '3.0' and python_version < '3.4')"}
        """
        lines = content.splitlines()[1:]
        initial_whitespace = len(lines[0]) - len(lines[0].lstrip())
        stripped = [line[initial_whitespace:] for line in lines]
        real_content = '\n'.join(stripped) + '\n'
        parsed = toml.loads(real_content)
        res = Pipfile.validate(parsed)
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
        requests = packages.pop('requests')
        self.assertEquals(requests.version, '*')
        self.assertEquals(dct, {})
