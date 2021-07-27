# Flowmon Rest Client

Python library for accessing Flowmon ADS and Flowmon Monitoring Center REST APIs.

## How to install

Python 3.6 or higher is required.

You can install Flowmon Rest Client with pip from local directory via:

```bash
$ pip install .
```

## How to use

There are two mandatory clients. Use `AdsClient` for accessing ADS API and `FmcClient` for Flowmon Monitoring Center API.

```python
from flowmonclient import AdsClient

flowmon = AdsClient(username="", password="", domain="https://collector2.csirt.muni.cz")

# Get all methods
methods = flowmon.methods.all()
from pprint import pprint
pprint(methods)

# Search events
from datetime import datetime, timedelta
now = datetime.now()
events = flowmon.events.search(from_timestamp=now - timedelta(weeks=1), to_timestamp=now, limit=2)
pprint(events)

# Get event detail
event_id = events[0]['id']
event_detail = flowmon.events.detail(event_id)
pprint(event_detail)
```

## Project organization

- `docs/` Contains official Flowmon documentation. The most up-to-date documentation can be found on [Flowmon Support Portal](https://support.flowmon.com/section.php?sid=121).
- `flowmonclient/AdsClient.py` Mandatory class for accessing Flowmon ADS API.
- `flowmonclient/FmcClient.py` Mandatory class for accessing Flowmon Monitoring Center API.
- `flowmonclient/AbstractClient.py` Creates https connection, takes care of authentication and provides convenient methods for making requests.
- `flowmonclient/cert/` Contains trusted CA certificate.
- `flowmonclient/resources/ads/` Contains classes for accessing individual ADS resources. Classes are organized based on ADS REST API Developer Guide - chapter 4 (Methods).
- `flowmonclient/resources/fmc/` Contains classes for accessing individual FMC resources. Classes are organized based on FlowMon REST API Developer Guide - chapter 6 (FlowMon Monitoring Center).
