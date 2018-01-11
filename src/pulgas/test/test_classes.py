import schema

import pulgas

@pulgas.config()
class Pipfile(object):

    @pulgas.config()
    class Source(object):

        url = pulgas.attrib(schema=str)
        verify_ssl = pulgas.attrib(schema=schema.Optional[bool])
        name = pulgas.attrib(schema=str)

    ## Copied from PEP 508, removed "extra"
    @pulgas.config()
    class Requires(object):

        os_name = pulgas.attrib(schema=str)
        sys_platform = pulgas.attrib(schema=str)
        platform_machine = pulgas.attrib(schema=str)
        platform_python_implementation = pulgas.attrib(schema=str)
        platform_release = pulgas.attrib(schema=str)
        platform_system = pulgas.attrib(schema=str)
        platform_version = pulgas.attrib(schema=str)
        python_version = pulgas.attrib(schema=str)
        python_full_version = pulgas.attrib(schema=str)
        implementation_name = pulgas.attrib(schema=str)
        implementation_version = pulgas.attrib(schema=str)

    @pulgas.config()
    class Packages(object):

        packages = pulgas.attrib(default=attr.Factory(dict))

        @classmethod
        def __pulgas_from_config__(cls, config):
            my_schema = schema.Schema({str:
                                       schema.Or(str, # Should be version str
                                                 schema.Use(PackageSpec))})
            validated_config = my_schema.validate(config)
            packages = {name: PackageSpec(version=value)
                              if isinstance(value, str)
                              else value}

    source = pulgas.attrib(schema=[schema.Use(Source)],
                           default=Source(url='https://pypi.python.org/simple',
                                          verify_ssl=True,
                                          name='pypi'))

    requires = pulgas.attrib(schema=schema.Optional(schema.Use(Requires)))

    packages = pulgas.attrib(schema=schema.Optional(schema.Use(Packages)))

    dev_packages = pulgas.attrib(schema=schema.Optional(schema.Use(Packages)))

class ClassTest(unittest.TestCase):

    def test_simple_pipfile(self):
        contents = """
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
        lines = content.splitlines()
        initial_whitespace = len(line[0]) - len(line[0].lstrip())
        stripped = [lines[initial_whitespace:] for line in lines]
        real_content = '\n'.join(stripped) + '\n'
        raise ValueError(real_content)
