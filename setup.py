#################################################################
#################################################################

# Author: martinja
# Contact: javier.martinez.samblas@cern.ch

#################################################################
#################################################################

# IMPORTS

from pathlib import Path
from setuptools import setup, find_packages
from distutils.command.install import INSTALL_SCHEMES
import os
import ast
import subprocess

#################################################################
#################################################################

# FUNCTIONS

def get_requirements_from_file(filename='requirements.txt'):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

def get_version_from_init(name):
    init_file = os.path.join(
        os.path.join(
            os.path.dirname(__file__), name, "__init__.py"
        )
    )
    with open(init_file, "r") as fd:
        for line in fd:
            if line.startswith("__version__"):
                return ast.literal_eval(line.split("=", 1)[1].strip())

#################################################################
#################################################################

# INPUTS

NAME = 'davit'
NAME_UNDERSCORED = NAME.replace("-","_")

VERSION = get_version_from_init(name=NAME_UNDERSCORED)

HERE = Path(__file__).parent.absolute()

SHORT_DESCRIPTION = "Data Analysis and Visualization Tool (DAVIT)."

with (HERE / 'README.md').open('rt', encoding='utf-8') as fh:
    LONG_DESCRIPTION = fh.read().strip()

#################################################################
#################################################################

# ADD THE LIBRARIES HERE

REQUIREMENTS: dict = {
    'core': get_requirements_from_file(),
    'test': [
        'pytest',
    ],
    'dev': [
        # empty,
    ],
    'doc': [
        'sphinx',
        'acc-py-sphinx',
    ],
}

#################################################################
#################################################################

for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

# CALL TO THE SETUPTOOLS LIBRARY THAT WILL GENERATE THE DIST

setup(
    name=NAME,
    version=VERSION,
    author='martinja',
    author_email='javier.martinez.samblas@cern.ch',
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://gitlab.cern.ch/bisw-python/{}'.format(NAME),
    packages=find_packages(),
    python_requires='>=3.11',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=REQUIREMENTS['core'],
    extras_require={
        **REQUIREMENTS,
        # The 'dev' extra is the union of 'test' and 'doc', with an option
        # to have explicit development dependencies listed.
        'dev': [req
                for extra in ['dev', 'test', 'doc']
                for req in REQUIREMENTS.get(extra, [])],
        # The 'all' extra is the union of all requirements.
        'all': [req for reqs in REQUIREMENTS.values() for req in reqs],
    },
    include_package_data=True,
)

#################################################################
#################################################################
