#!/usr/bin/python3

from setuptools import setup

setup(
    name='criticality_estimator',
    version='0.1',
    author='CSIRT-MU',
    description='Criticality Estimator',
    packages=['criticality_estimator'],
    package_dir={'criticality_estimator': 'src'},
    python_requires='>=3.7',
    install_requires=['structlog', 'setuptools']
    )

