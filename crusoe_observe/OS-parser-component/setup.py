#!/usr/bin/python3

from setuptools import setup, find_packages

setup(
    name='osrest',
    version='0.1',
    description='os detection from flows',
    packages=find_packages(),
    package_data={'osrest': ['data/*']},
    install_requires=['setuptools', 'structlog', 'scikit-learn', 'pandas'],
    )
