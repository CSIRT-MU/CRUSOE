#!/usr/local/bin/python3.6

from setuptools import setup, find_packages

setup(
    name='rtir_connector',
    version='0.1',
    description='connector for RTIR',
    package_data={'rtir_connector': ['certs/cert_file.crt']},
    include_package_data=True,
    packages=find_packages(), install_requires=['structlog', 'pytz', 'requests', 'pytest']
)

