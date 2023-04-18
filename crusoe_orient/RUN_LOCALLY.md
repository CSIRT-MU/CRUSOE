# Running (building) the project locally

## Prerequisites

### Node.js

Angular requires Node.js (at least v10) to be installed.

- To check your version, run `node -v` in a terminal/console window.
- To get Node.js, go to [nodejs.org](https://nodejs.org/en/download/).

If your Node.js version is 16 or higher, then set this environment variable:

$ export NODE_OPTIONS=--openssl-legacy-provider

### npm package manager

NPM client command line interface is installed with Node.js by default.

## Installing npm dependencies

Before running development server or building the project, you need to install dependencies listed in `package.json` file located in the project root folder. Install those dependencies by running `npm install` in your terminal/console.

## Ensure API endpoints are set correctly

Before building/serving the project, make sure that file `src/environments/environment.prod.ts` (or `src/environments/environment.ts` if you're serving project using `ng serve`) contains proper API urls.

## Development server

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.

## Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory. Use the `--prod` flag for a production build.

## Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

## Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI README](https://github.com/angular/angular-cli/blob/master/README.md).
