from setuptools import setup, find_packages

setup(
    name='NETlist_connector',
    version='0.2',
    description='Parser for subnets and contacts',
    author='CSIRT-MU',
    keywords='module contact subnet crusoe',
    package_data={'NETlist_connector': ['data/subnets_data.txt']},
    packages=find_packages(),
    install_requires=['structlog', 'requests', 'netaddr', 'dnspython'],
)
