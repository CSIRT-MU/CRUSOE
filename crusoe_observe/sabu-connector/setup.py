#!/usr/bin/python3

from setuptools import setup, find_packages

setup(
    name='sabu',
    version='0.1',
    description='parsing json messages and storing data into Neo4j',
    packages=find_packages(),
    install_requires=['structlog']
)
