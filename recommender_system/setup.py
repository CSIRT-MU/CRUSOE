#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='recommender-system',
    version='1.0',
    url='https://gitlab.fi.muni.cz/xboucek/recommender-system-for-ransomware'
        '-mitigation',
    license='',
    author='Vladimír Bouček',
    author_email='xboucek@mail.muni.cz',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    description='',
    install_requires=[
        'neo4j>=4.3.7',
        'djangorestframework>=3.13.1',
        'Django>=4.1',
        'django-cors-headers>=4.0'
    ]
)