# Flowmon connector

Temporary connector for collector until Flowmon fixes rest limit.

## Design

Whole logic of the connector is included in `flowmon_connector.py`. This file includes methods for downloading data from collector.

## Required packages/versions

At least Python3.6.

flowmon-rest-client - available at root directory.

Required packages are specified in setup.py and they will be installed when you use one of the installation methods below.

## Usage

### Install

```bash
$ pip install .
```

### Running

```python
from flowmon_m import flowmon_connector

flowmon_connector.download_rest(output_file="", password="")
flowmon_connector.download_ssh(key_path="", password="")

```


