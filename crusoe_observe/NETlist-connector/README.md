# NETlist-connector
This component is responsible for continuous updates of domain names corresponding to IP addresses. On top of that it updates information about subnets as well as responsible contacts and organization units.

## Design
Component consists of following three files:
1. `contacts.py` is responsible for adding contacts for the subnets.
2. Task of the `dopmains.py` is to resolve ip-domain pairs
3. `subnetParser.py` finds the subnets and communicates with the database instance.


## Required packages/versions

At least Python3.7.

Required packages are specified in setup.py and they will be installed when you use one of the installation methods below.

Next, a working Neo4j database is required.

Lastly, neo4j-client is required, available at root directory.

## Usage

### Install :

```bash
$ pip install .
```

### Running
```python
>>> from NETlist_connector.subnetParser import NETlist

>>> nl = NETlist("neo4_password", "path to neo4j import directory", logger=logger)
>>> nl.update()
```
