# REST API for Neo4j database

This `neo4j_rest` Django project is a Django REST API which should be used for automated 
interaction with Neo4j database containing data conforming to the CRUSOE data model.
Enpoints listed in `views.py` can be used to retrieve or manipulate with various types of nodes in the database
(e.g., events, software, cves, IPs) or to interact with PAOs of Act phase. Complete overview of endpoints is 
listed in swagger (TODO link). 

### Design
The project consists of one django application (situated in `crusoe_django` folder) with typical structure. The most important modules are:  
* **settings.py** which contains settings for this Django project
* **urls.py** which contains all of the available endpoints (URLs)
* **views.py** which contains underlying functionality for each endpoint
* **conf.ini** which contains configuration options.

### Required packages/versions

At least `Python3.6`.

The project requires `Django` and `Django REST Framework`.

Further, `neo4j-client` (another CRUSOE component) is required, see https://gitlab.ics.muni.cz/CRUSOE/neo4j-client. 

### Usage

#### Install

Clone the repository with HTTPS:

```
git clone https://gitlab.ics.muni.cz/CRUSOE/neo4j-rest.git
```


#### Running

Start the application with:

```
python3 django/manage.py runserver
```
