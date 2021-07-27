# Filler orchestration service
This repository contains orchestration service for CRUSOE project.   
It's purpose is to automatically run CRUSOE components based on preconfigured options.

## Design
This repository consist of following items:

1. Directory `config` contains config file with values used by the orchestration service. You should define, set your own values.
2. `celery_logger.py` is logger instance used by the orchestration service.
3. `celeryconfig.py` defines celery options and intervals in which each component should run.
4. `crusoe.py` contains definition of tasks which will be run.

## Required packages/versions
At least Python3.7.

Required packages are specified in `requirements.txt` and can be installed using:
```bash
pip install -r requirements.txt
```

Next, a working Neo4j database with `graph algorithms` and `apoc` plugins is expected.

Lastly, CRUSOE components need to be installed and configured properly. Following components are required:

    CRUSOE/services-component  
    CRUSOE/NETlist-connector  
    CRUSOE/neo4j-client  
    CRUSOE/cms-component  
    CRUSOE/cve-connector  
    CRUSOE/criticality-estimator  
    CRUSOE/decide-component  
    CSIRT-MU/flowmon-rest-client  
    CRUSOE/flowmon-connector  
    CRUSOE/nmap-topology-scanner  
    CRUSOE/OS-parser-component  
    CRUSOE/RTIR-connector  
    CRUSOE/sabu-connector  
    CRUSOE/vulnerability-component  
    CRUSOE/webchecker-component  
    CRUSOE/attack-graph-component  
    CRUSOE/act-overseer  

## Usage

### Install/setup
1. Clone this repository  
2. Copy config and fill it with your values
```bash
$ cp conf/confi.ini.example conf/conf.ini
```

### Running

run celery/flower as script with following command:
```bash
# celery -A crusoe worker -B -l=INFO
# celery flower -A crusoe --broker=redis://localhost:6379/0
```
