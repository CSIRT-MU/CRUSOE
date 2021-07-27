# Running (building) the project using Docker

## Prerequisites

### Docker

- To check your version, run `docker -v` in a terminal/console window.
- To get Docker, go to [docs.docker.com/get-docker](https://docs.docker.com/get-docker/).

## Ensure API endpoints are set correctly

Before building the image, make sure that file `src/environments/environment.prod.ts` contains proper API urls.

## Building Docker image

Build docker image by running `docker build --no-cache -t crusoe_dashboard .` in your terminal/console.

## Run Docker image as a container

Now it's time to run the image we built. Run `docker run --name crusoe_dashboard -d -p 4200:80 crusoe_dashboard`. Navigate to `http://localhost:4200/` to visit the application.
