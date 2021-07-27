# RTIR Connector
RTIR Connector is CRUSOE component developed for parsing relevant information about tickets from RT system.

## Design
Component consist of one file:
1. `rtir.py` contains methods responsible for downloading data from RT system, parsing relevant information and preparing JSON with output.

## Required packages/versions
At least `Python3.7`.

Required packages are specified in `setup.py` and they will be installed when you use one of the installation methods below.

If the component will be installed alone - using one of the methods in section `Install` (not as a part of CRUSOE ansible), the following steps needs to be done:
1. Copy content of `certs/` to the `/usr/local/share/ca-certificates/`. (2 CA files)
2. Update list of trusted CA using `sudo update-ca-certificates` (Adds the certificates to list of trusted CAs)

## Usage

### Install

```bash
$ pip install .
```

### Running
```python
>>> from rtir_connector import rtir

# default usage
>>> rtir.parse_rt(user, password)

# customizable usage
>>> rtir.parse_rt(user, password, output='/var/lib/neo4j/import/rtir.json', uri='https://rt.csirt.muni.cz/REST/1.0',
             subnet_filter="CF.{IP} >= '147.251.' AND CF.{IP} < '147.252.'", last_day=True, logger=structlog.get_logger())
```
