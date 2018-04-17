#!/usr/bin/env python
# coding: utf-8

import re
from setuptools import setup

# Parse the version and release from the spec file
with open('fmf.spec') as specfile:
    lines = "\n".join(line.rstrip() for line in specfile)
    version = re.search('Version: (.+)', lines).group(1).rstrip()
    release = re.search('Release: (\d+)', lines).group(1).rstrip()

# acceptable version schema: major.minor[.patch][sub]
__version__ = '.'.join([version, release])
__pkg__ = 'fmf'
__pkgdir__ = {}
__pkgs__ = ['fmf']
__provides__ = ['fmf']
__desc__ = 'Flexible Metadata Format'
__scripts__ = ['bin/fmf']
__irequires__ = [
    'PyYAML',
]

pip_src = 'https://pypi.python.org/packages/source'
__deplinks__ = []

# README is in the parent directory
readme = 'README.rst'
with open(readme) as _file:
    readme = _file.read()

github = 'https://github.com/psss/fmf'
download_url = '{0}/archive/master.zip'.format(github)

default_setup = dict(
    url=github,
    license='GPLv2',
    author='Petr Splichal',
    author_email='psplicha@redhat.com',
    maintainer='Petr Splichal',
    maintainer_email='psplicha@redhat.com',
    download_url=download_url,
    long_description=readme,
    data_files=[],
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
    ],
    keywords=['metadata', 'testing'],
    dependency_links=__deplinks__,
    description=__desc__,
    install_requires=__irequires__,
    name=__pkg__,
    package_dir=__pkgdir__,
    packages=__pkgs__,
    provides=__provides__,
    scripts=__scripts__,
    version=__version__,
    entry_points={
        'console_scripts': [
            'fmf-output = fmf.output_interpreter:main'
        ]
    },
)

setup(**default_setup)
