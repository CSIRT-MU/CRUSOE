# Act overseer

Act overseer works as a cenral point of phase ACT fot other phases. Module runs on CRUSOE server and is executed by Celery.

## Design

Act-overseer consists of python files for modules and a data directory for configuration.
1. act_to_neo4j.py - Calls PAO wrappers and updates the PAO properties in neo4j database using its REST API.
2. decide_to_act.py - Module contains executive functionality of act overseer.
3. act_overseer_rest_api - Module provides enpoints for manual execution of actions and parameter configuration of act overseer.
4. data - Contains certificate used for verification of servers identity and act overseer config.

## Required packages/versions

Python 3.7+.

Required packages are specified in setup.py and they will be installed when you use one of the installation methods below.

Next, a working Neo4j database is expected.

If you are setting this component on your own server, you need to replace ```data/cert.crt``` with your certificate chain and update REST calls in the code to match your own endpoints.


## Usage

### Install

```bash
pip install setup.py
```

### Running

```python
>>> from act_overseer import decide_to_act

>>> decide_to_act.run_decide_to_act(user, passw, missions_and_configurations, logger, dashboard_log, server_url)
```

user and pass are credentials to authenticate when trying to send request to neo4j REST API. missions_and_configurations is a json containing missions and configurations. server_url is url or IP of a server with running database rest api.
