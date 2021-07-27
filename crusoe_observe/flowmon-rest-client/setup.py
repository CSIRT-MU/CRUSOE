# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path


# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='flowmon-rest-client',
    description='Flowmon API Client Library for Python',
    long_description=long_description,
    author='CSIRT-MU',
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='flowmon rest api',
    packages=find_packages(exclude=['docs']),
    install_requires=['requests-oauthlib==1.1.0'],
    python_requires='>=3.6',
    package_data={
        'flowmonclient': ['cert/*'],
    },
)
