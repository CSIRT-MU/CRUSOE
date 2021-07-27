// The file contents for the current environment will overwrite these during build.
// The build system defaults to the dev environment which uses `environment.ts`, but if you do
// `ng build --env=prod` then `environment.prod.ts` will be used instead.
// The list of which env maps to which file can be found in `.angular-cli.json`.

import * as packageData from '../../package.json';

export const environment = {
  applicationName: 'CRUSOE Dashboard',
  production: false,
  version: packageData.version,
  apiUrl: 'https://crusoe.csirt.muni.cz/redirect-api/redirect/',
  tmpActApi: 'https://crusoe.csirt.muni.cz/act/',
  graphqlApi: 'https://crusoe.csirt.muni.cz/graphql-api/graphql',
  firewallApi: 'https://crusoe-worker.csirt.muni.cz/firewall',
};
