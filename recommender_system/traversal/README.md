# Recommender traversal procedure

## About
Traversal procedure created in Neo4j Traversal Framework for finding nearby 
hosts in the network to given maximum distance. Compiled procedure must be 
added to the Neo4j database instance to use recommender system properly.

## Requirements
- JDK 11
- Apache Maven, tested with Maven 3.8.1

## Install
Traversal procedure can be compiled with Maven using:
    
    mvn clean install

Compiled .jar plugin can then be installed into Neo4j database instance by
moving it inside plugins folder:

    neo4j-community-4.3.3/plugins/traverse-plugin.jar

After database restart, traversal procedure can be used via Cypher query
language. 

Example:

    CALL traverse.findCloseHosts(127.0.0.1, 2)