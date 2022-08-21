# Recommender system for ransomware mitigation

## About


## Requirements
Recommender needs at least Python 3.10 with following packages:
- neo4j >= 4.3.7
- djangorestframework >= 3.13.1 
- Django >= 4.1

In case of using only as a console script, Django and rest framework can 
be omitted.

To run the Neo4j 4.0.0+ database , Java in version 11 must be installed.

## Install 
Recommender can be easily installed as a Python packages with pip. 
To run recommender in a local virtual environment, run (in root of this project):

    python3 -m venv venv
    source bin/activate (Unix) / venv\Scripts\activate.bat (Win)
    pip install -e .


## Running the Neo4j database
To start the database, run (inside neo4j root directory):
    
    ./bin/neo4j console

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

Connection information to the Neo4j database (NEO4J_URL, NEO4J_USER and NEO4J_PASSWORD) 
must be set in environment variables.

Recommender can also be used as a REST API:

    python src/backend/manage.py runserver {port}

Connection information to the Neo4j database must be specified in Django's settings.py file:

    DATABASES = {
        "default": {
            "URL": "...",
            "USER": "...",
            "PASSWORD": "...",
        }
    }

API Endpoints:

    recommender/attacked-host

GET: Returns information about attacked host. Requires "ip" or "domain" in a query parameter.
    
    recommender/recommended-hosts

GET: Returns recommended hosts. Requires "ip" or "domain" in a query parameter.
    
    recommender/configuration
 
GET: Returns currently used recommender configuration (if there is any).

PUT: Sets new configuration, requires new configuration as a JSON in body of the request.
