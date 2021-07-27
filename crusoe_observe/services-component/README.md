# Services Component
Services component is a CRUSOE component designed for detection of services
running on network devices via analysis of network flow records.

## Design
Component consists of following items:

1. `src/data` contains additional data files required by the component or subcomponents.
2. `run.py` executes individual service detection subcomponents, combines their results, and produces a new session file.
3. `core.py`  contains implementation of `Result` object, which comprises `Hierarchy` for each observed device (IP). The `Hierarchy` object follows
subpart of CPE identification (vendor:product:version). The hierarchy contains
a tree whose levels consist of objects `Vendor`, `Product`, and `Version`. This
structure is designed for of results of individual detection methods, and
additional processing. Each subcomponent should use these classes to simplify
interaction with other parts of the component. `Result` class holds a mapping
between IP's detected software and associated `Hierarchy` object.
4. `rules.py` is designed for simplifying identification of services using
rule-based processing of network flow records. It provides `Rules` object,
which is initialized by a set of pre-configured rules, which are afterwards
used for matching against the flows.

## Required packages/versions

At least Python3.7.

Required packages are specified in setup.py and they will be installed when you use one of the installation methods below.

## Usage

### Install

```bash
$ pip install .
```

### Running

```python
>>> import services_component
>>> services_component.run(flow_path, session_path)
'New sessions: 157, active sessions: 308'
```
