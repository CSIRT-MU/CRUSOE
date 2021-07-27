# Webchecker Component

Task of this component is to perform detection of unknown domain names and
assigned IPs within local network from incoming HTTP traffic and once per day
check X509 certificates of such servers.

## Design
Component consist of one file:
1. `core.py` contains one class with all the methods required for successful detections.

## Required packages/versions
At least `Python3.7`.

Required packages are specified in `setup.py` and they will be installed when you use one of the installation methods below.

## Usage

### Install

```bash
$ pip install .
```

### Config options
Config object can be an empty dictionary, or an dictionary containing specific fields:
- "ignore" - List of IP ranges to ignore during `run_certs` method call.
- "target_network" - List of IP ranges to record during `run_detect` method call.

### Running
```python
>>> from webchecker_component import Webchecker
>>> wc = Webchecker(config, logger_object) # if no logger supplied, structlog PrintLogger is used

# inspect certificates of hostnames
>>> wc.run_certs(hostnames) # hostnames: iterable of pairs of ips and hostnames; or just iterable of hostnames(no IP ranges ignored)

# scan flows for new domain names
>>> wc.run_detect(flows) # flows: path to input flows
```
