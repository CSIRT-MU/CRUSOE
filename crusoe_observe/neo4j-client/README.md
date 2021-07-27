# Neo4j Client
Neo4j Client is a CRUSOE component that contains database queries required by other CRUSOE components.

## Design
Component is split into 2 directories:
1. `neo4jclient` directory contains Cypher queries for every subcomponent of the CRUSOE project.
2. `test` directory contains tests for the cypher quries.

## Required packages/versions

At least `Python3.7`.  

Required packages are specified in `setup.py` and they will be installed when you use one of the installation methods below.

Next, a working Neo4j database with graph algorithms and APOC plugins is expected.

Lastly, database must allow imports from files, add `apoc.import.file.enabled=true` to your database settings file.

## Usage

### Install

```bash
$ pip install .
```

### Running

```python
from neo4jclient import <ClientYouWantToUse>

client = <ClientYouWantToUse>.<ClientYouWantToUse>(password="neo4jPassword")

client.<MethodYouWantToUse>

```
