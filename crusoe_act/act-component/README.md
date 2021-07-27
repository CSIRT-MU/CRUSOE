# PAO Wrappers for ACT

This component provides specification and implementation of the PAO wrapper layer for the ACT phase. 

## Design

Act-pao-wrappers repository consists of 5 wrappers coded in Python using Django framework. 6th wrapper, simulated-pao-firewall,
was used for testing only.
1. wrapper folders - contain the implementation of the wrappers
2. specification - contains the specification of functions supported by each wrapper

## Specification

Specification of the required API functions of each wrapper are detailed in the folder /specification/

## Required packages/versions

Python version: 3.7+.
Django version 3.1.4+.
djangorestframework 3.12.1+.

## Usage

Clone the repository or download it. Each wrapper can be run with 
```bash
python3 manage.py runserver
```
inside the directory of the wrapper.

One can also run the wrapper using apache webserver. Tutorials on how to do it can be found on the internet.
