# Criticality Estimator

Task of this component is to _execute_ computations on a database with the goal
of discovering the most critical nodes based on their centrality. The results
are stored within the database, therefore _no actual data is exported_ by this
component.

## Design

Component consist of one file:
1. `core.py` is used for computations of criticality(importance) of nodes in database.

Component currently allows for computation of:
- topology betweenness centrality
- topology degree centrality
- dependency degree centrality


## Required packages/versions

At least Python3.7.

Required packages are specified in setup.py and they will be installed when you use one of the installation methods below.

Next, a working Neo4j database with `graph algorithms` plugin is expected.

Lastly, neo4j-client is required, see neo4j-client.

## Usage

### Install

```bash
$ pip install .
```

## Running
```python
>>> from criticality_estimator import CriticalityEstimator
>>> ce = CriticalityEstimator(bolt="bolt://localhost:7687", password="test", logger=logger)
>>> ce.run()
'Criticality: topology betweenness 128 nodes; topology degree 128 nodes; dependency degree 128 nodes.'
```
