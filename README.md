# Recommender system for ransomware mitigation

## About
Recommender system for ransomware mitigation is a data-driven service for 
finding hosts in the network, which are similar or close to the attacked host. 
Recommendations are based on Neo4j graph database containing contextual
information about the network.

## Requirements
Recommender needs at least Python 3.10 with following packages:
- neo4j >= 4.3.7
- djangorestframework >= 3.13.1 
- Django >= 4.1

In case of using only as a console script, Django and rest framework can 
be omitted.

To run the Neo4j 4.0.0+ database, Java in version 11 must be installed.

## Install 
Recommender can be easily installed as a Python packages with pip. 
To run recommender in a local virtual environment, run (in root of this 
project):

    python3 -m venv venv
    source bin/activate (Unix) / venv\Scripts\activate.bat (Win)
    pip install -e .


## Running the Neo4j database
To start the database, run (inside neo4j root directory):
    
    ./bin/neo4j console

Database is not provided with the tool (creating a dataset is planned for future work). So far, you can use CRUSOE toolset by CSIRT-MU to populate your own database or consult the developers of this tool about the status of publicly available dataset or artificial data.

## Usage
Recommender can be used as a console script:

    python src/script/main.py -i 127.0.0.1

With following options:

    -i | --ip      -> IP input
    -d | --domain  -> domain input
    -p | --path    –> config path (if not given, default config is used)
    -l | --limit   –> number of hosts to print on output
    -v | --verbose -> use verbose stdout print
    -c | --csv     -> path for export in csv
    -j | --json    –> path for export in json
    At least domain or ip is reuqired.

Connection information to the Neo4j database (NEO4J_URL, NEO4J_USER and 
NEO4J_PASSWORD) must be set as environment variables.

Recommender can also be used as a REST API:

    python src/backend/manage.py runserver {port}

In this case, connection information to the Neo4j database must be 
specified in the Django's settings.py file:

    DATABASES = {
        "default": {
            "URL": "...",
            "USER": "...",
            "PASSWORD": "...",
        }
    }

API Endpoints:

    recommender/attacked-host

GET: Returns information about attacked host. Requires "ip" or "domain" 
in a query parameter.
    
    recommender/recommended-hosts

GET: Returns recommended hosts. Requires "ip" or "domain" in a query parameter.
    
    recommender/configuration
 
GET: Returns currently used recommender configuration (if there is any).

PUT: Sets a new configuration, requires new configuration as a JSON in 
body of the request.

PATCH: Calculates mean critical bounds where possible and updates configuration

## Help utilities
Package utils contains calculator, which can calculate critical bounds 
(if partial similarity is higher than this bound, warning message is created). 
For CPE similarities, it uses mean of all CPE combinations found in the 
database (for the same type of software component). For cumulative 
similarities, it calculates mean number of events/vulnerabilities 
found on the hosts and divides it by total number of events/vulnerabilities 
in the database. It can be run as a script:

    python src/utils/mean_bound_calculator.py path_to_config_json

Or via API as the PATCH method of configuration endpoint.

## References and Acknowledgements

The tool was originally implemented by Vladimír Bouček in his bachelor's thesis under the supervision of Martin Husák. The thesis (in Czech language) can be found at: https://is.muni.cz/th/vl4k7/

The original idea for this tool was proposed by Martin Husák in the paper "Towards a Data-Driven Recommender System for Handling Ransomware and Similar Incidents" presented at IEEE ISI 2021 conference. Check the paper and slides at:
https://www.muni.cz/en/research/publications/1800767

The tool design and development were described by Vladimír Bouček and Martin Husák in the paper "Recommending Similar Devices in Close Proximity for Network Security Management" presented at the WiMob 2023 conference. Check the paper and slides at:
https://www.muni.cz/en/research/publications/2287837
