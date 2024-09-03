from setuptools import setup, find_packages

setup(
    name='crusoe_decide',
    version='1.0',
    description='decision support using attack graphs',
    author='CSIRT-MU',
    keywords='attack graph crusoe decide',
    packages=find_packages(),
    package_data={'crusoe_decide': ['data/*']},
    install_requires=['pgmpy==0.1.6', 'neo4j', 'structlog', 'wrapt']
)
