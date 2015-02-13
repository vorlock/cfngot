from setuptools import setup
from setuptools import find_packages
import os.path


def find_version(path):
    import re
    version_file = open(path).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(name='cfngot',
      version=find_version(os.path.join(os.path.dirname(__file__), 'cfngot')),
      packages=find_packages(),
      include_package_data=True,
      entry_points={'console_scripts': []},
      install_requires=['Jinaj2 >= 2.7.3',
                        'pyyaml >= 3.11',
                        'awscli >= 1.4.2',
                        'docopt >= 0.6.2',
                        ],
      license='The MIT License (MIT))',
      description='Tool for generating cloudformation templates out of jinja2',
      long_description='''It's tool allowing for describing cloudformation
templates with jinja2 formating. J2 templates will be then rendered to the pure
json cloudformation templates.
This tool also allows for comparing two json files (json-diff subcommand),
creating (new) and updating (already existing) CFN stacks on AWS accounts
configured with profiles in awscli tool.
''',
      author='Marcin Kulisz',
      author_email='sourceforge@kulisz.net',
      url='http://www.python.org/sigs/distutils-sig/',
     )
