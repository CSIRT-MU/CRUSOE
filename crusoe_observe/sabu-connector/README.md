# SABU connector

SABU connector receives IDEA messages containing information about vulnerabilities found within Masaryk University network from system Warden (* https://warden.cesnet.cz//en/index). 
Connector parses the message and saves information into Neo4j database. It is possible to change IP regex in celery config so you are not restricted to only receive vulnerabilities 
within Masaryk University network.

## Design

Connector consists of a single file JsonParsing.py. It checks for a running instance of Warden system, then starts parsing messages
received from Warden. These messages are of type IDEA described <a href="https://idea.cesnet.cz/en/index
">here</a>). After all messages are parsed, data obtained are sent to neo4j database (e.g. IP of the attacker, description of the event).

## Required packages/versions
Python 3.7+

Required packages are specified in setup.py and will be installed when you use one of the installation methods below.

You need to have a running Warden system for sabu-connector to work properly. 
To achieve this, visit https://warden.cesnet.cz/ and apply for permission to
receive Warden messages (how to do that is described <a href="https://warden.cesnet.cz/cs/participation
">here</a>). 

You will also need a running neo4j database to store parsed data from warden messages.
Once you set Warden configs to satisfy your needs and have running Warden and neo4j, you can run sabu-connector.

## Usage

### Install

```bash
$ pip install .
```

### Running

``` python
>>> from sabu import JsonParsing

>>> JsonParsing.parse(directory="/directory/with/received/messages/", 
                     passwd="neo4jpassword", regex="IPRangeMU", 
                     path_to_warden_filer_receiver="/path/to/warden/receiver/", 
                     path_to_neo4j="/directory/to/save/json/")
```

#### Parameters description

`directory` = in Warden config (`warden_filer.cfg`), you have to specify where 
the messages are going to flow from Warden system (e.g. "/var/warden_receiver")
In this 'directory', three seperate directories will be created by Warden:
`errors`, `incoming` and `temp`. You will find received messages in the `incoming`.

`passwd` = Password required to connect to neo4j database.

`regex` = Regular expression used to filter messages with given IP prefix in it
(e.g. `147\.251\.[0-2]?[0-9]?[0-9]\.[0-2]?[0-9]?[0-9]?` for Masaryk University
network.)

`path_to_warden_filer_receiver` = This path is used to check whether Warden is
running or not. If not, it will try to restart it and upon unsuccessfull restart
raise an custom WardenException.

`path_to_neo4j` = Directory in which the final JSON with parsed data from received
messages is stored and processed by neo4j client. Neo4j client si a custom script
consisting of Cypher commands, where Cypher is a Neo4j's graph query language.
