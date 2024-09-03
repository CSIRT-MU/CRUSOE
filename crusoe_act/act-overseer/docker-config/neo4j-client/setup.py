from setuptools import setup

setup(
        name='neo4jclient',
        version='0.2',
        description='neo4j library for crusoe',
        author='CSIRT-MU',
        keywords='crusoe neo4j',
        install_requires=['neo4j-driver==1.7', 'pytest', 'neo4j'],
        python_requires='>=3.6',
        packages=['neo4jclient']
        )
