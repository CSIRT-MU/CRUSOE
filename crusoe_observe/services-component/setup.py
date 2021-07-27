#!/usr/bin/python3

from setuptools import setup

setup(
    name='services_component',
    version='0.2',
    author='CSIRT-MU',
    description='Services detection using flows',
    packages=['services_component', 'services_component.services'],
    package_dir={'services_component': 'src'},
    package_data={'services_component': ['data/*']},
    python_requires='>=3.6',
    install_requires=['joblib', 'numpy', 'pandas', 'sklearn', 'structlog']
    )
