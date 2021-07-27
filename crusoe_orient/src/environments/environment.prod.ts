import * as packageData from '../../package.json';

export const environment = {
  applicationName: 'CRUSOE Dashboard',
  production: true,
  version: packageData.version,
  /* Redirect API URL */
  apiUrl: 'https://crusoe.csirt.muni.cz/redirect-api/redirect/',
  /* Act API URL */
  tmpActApi: 'https://crusoe.csirt.muni.cz/act/',
  /* GraphQL API URL */
  graphqlApi: 'https://crusoe.csirt.muni.cz/graphql-api/graphql',
  /* Firewall API URL */
  firewallApi: 'https://crusoe-worker.csirt.muni.cz/firewall',
};
