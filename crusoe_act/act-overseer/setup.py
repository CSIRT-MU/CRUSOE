from setuptools import setup, find_packages

setup(
    name='act_overseer',
    version='0.1',
    description='Monitors the PAOs and manages the PAO data in neo4j db',
    packages=find_packages(),
    package_data={'act_overseer': ['data/cert_file.crt', 'data/act_overseer_config']},
    include_package_data=True,
    install_requires=['requests', 'structlog', 'django', 'djangorestframework']
)
