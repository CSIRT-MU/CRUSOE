#!/usr/bin/python3

from setuptools import setup

setup(
    name='webchecker_component',
    version='0.1',
    author='CSIRT-MU',
    description='Webchecker Component',
    packages=['webchecker_component'],
    package_dir={'webchecker_component': 'src'},
    python_requires='>=3.6',
    install_requires=['structlog', 'dnspython', 'setuptools']
    )
