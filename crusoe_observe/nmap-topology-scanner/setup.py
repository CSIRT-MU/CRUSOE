from setuptools import setup

setup(
    name='nmap_topology_scanner',
    version='0.6',
    description='CRUSOE tool for scanning the network topology using nmap',
    author='CSIRT-MU',
    keywords='scan nmap topology services crusoe',
    package_data={'nmap_topology_scanner':['data/*']},
    python_requires='>=3.6',
    packages=['nmap_topology_scanner'],
    install_requires=['python-nmap', 'structlog']
    )
