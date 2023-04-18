# Running (building) the project using Docker

## Prerequisites

### Docker

- To check your version, run `docker -v` in a terminal/console window.
- To get Docker, go to [docs.docker.com/get-docker](https://docs.docker.com/get-docker/).

## Ensure credentials are configured

Before building the image, make sure that neo4j credentials are set properly. See README.md for instructions on how to set credentials.

## Building Docker image

Build docker image by running `docker build --no-cache -t graphql_api .` in your terminal/console.

## Run Docker image as a container

Now it's time to run the image we built. Run `docker run --name graphql_api -d -p 4001:4001 graphql_api`. Navigate to `http://localhost:4001/graphql` to visit the GraphQL API.
