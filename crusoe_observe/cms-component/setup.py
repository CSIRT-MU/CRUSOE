#!/usr/bin/python3

from setuptools import setup, find_packages

setup(
    name='cmsscan',
    version='0.1',
    description='wrapper for whatweb',
    packages=setuptools.find_packages(),
    package_data={'cmsscan': ['data/cms.json']},
    install_requires=['structlog']
    )
