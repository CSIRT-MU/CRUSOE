from setuptools import setup

setup(
    name='flowmon-connector',
    version='0.1',
    packages=['flowmon_m'],
    install_requires=['paramiko==2.4.0', 'structlog']
    )
