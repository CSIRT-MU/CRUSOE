# Running (building) the project locally

## Prerequisites

### Node.js

Angular requires Node.js (at least v10) to be installed.

- To check your version, run `node -v` in a terminal/console window.
- To get Node.js, go to [nodejs.org](https://nodejs.org/en/download/).

### npm package manager

NPM client command line interface is installed with Node.js by default.

## Installing npm dependencies

Before running development server or building the project, you need to install dependencies listed in `package.json` file located in the project root folder. Install those dependencies by running `npm install` in your terminal/console.

## Ensure credentials are configured

Before building the image, make sure that neo4j credentials are set properly. See README.md for instructions on how to set credentials.

## Run server

Run `npm run start` to start a server. Navigate to `http://localhost:4001/graphql`.

## Run server in background

Run `npm run start:background` to start a server as a background process. Navigate to `http://localhost:4001/graphql`.
