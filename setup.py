#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine

import re
import io
import os
import sys
from shutil import rmtree

from setuptools import find_packages, setup, Command

NAME = 'dear.remote-integrity'
SLUG = NAME.replace('-', '_')
PATH = SLUG.replace('.', os.path.sep)
NAMESPACE = 'dear'

DESCRIPTION = (
    'The DearBytes remote integrity tool is an IDS (Intrusion '
    'Detection System) that keeps track of files on a remote '
    'server and logs an event if a file gets added, removed or modified.')

URL = 'https://github.com/DearBytes/Remote-Integrity-Tool'
EMAIL = 'info@dearbytes.nl'
AUTHOR = 'Luke Paris (Paradoxis) @ DearBytes'
REQUIRES_PYTHON = '>=3.6.0'

REQUIRED = [
    'appdirs==1.4.0',
    'axel==0.0.7',
    'certifi==2017.1.23',
    'cffi==1.9.1',
    'colorama==0.3.7',
    'colorlog==2.10.0',
    'cryptography==1.7.2',
    'future==0.16.0',
    'idna==2.2',
    'packaging==16.8',
    'paramiko==2.1.6',
    'pyasn1==0.2.1',
    'pycparser==2.17',
    'pyparsing==2.1.10',
    'python-telegram-bot==5.3.0',
    'six==1.10.0',
    'SQLAlchemy==1.1.5',
    'tabulate==0.7.7',
    'urllib3>=1.23',
    'virtualenv==15.1.0',
]

EXTRAS_REQUIRE = {
    'dev': [
        'twine',
        'wheel',
        'setuptools>=40.6.3'
    ]
}

ENTRY_POINTS = {
    'console_scripts': [
        'remote-integrity=dear.remote_integrity.__main__:main',
    ]
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = ('\n' + f.read()).strip()

with io.open(os.path.join(here, PATH, '__init__.py'), encoding='utf-8') as init:
    VERSION = re.search(r'__version__ = [\'"]([\d.]+)[\'"]', init.read()).group(1)

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    with open(os.path.join(here, NAME, '__version__.py')) as f:
        exec(f.read(), about)
else:
    about['__version__'] = VERSION


# Where the magic happens:
setup(
    name=NAME,
    namespace_packages=[NAMESPACE],
    packages=[SLUG],
    version=about['__version__'],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    extras_require=EXTRAS_REQUIRE,
    entry_points=ENTRY_POINTS,
    install_requires=REQUIRED,
    include_package_data=True,
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ]
)
