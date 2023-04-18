# GraphQL API for Neo4j

GraphQL API endpoint based on [GRANDstack Starter](https://grandstack.io/)

## Configure

Before running the project, you should set your Neo4j connection string and credentials in `src/db_config.js` (fill and rename `db_config.js.template` file) or in `.env`. For example:

_.env_

```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=letmein
```

In case of using Vagrant, you should set credentials in `playbook.yml` file.

## Running (and building) the project

### Run project using Docker

See guide [(RUN_DOCKER.md)](RUN_DOCKER.md) on how to run project using Docker.

### Run project using Vagrant

See guide [(RUN_VAGRANT.md)](RUN_VAGRANT.md) on how to run project using Vagrant.

### Run project locally

See guide [(RUN_LOCALLY.md)](RUN_LOCALLY.md) on how to run project locally.

## Deployment

You can deploy to any service that hosts Node.js apps.
