import * as packageData from '../../package.json';

export const environment = {
  applicationName: 'CRUSOE Dashboard',
  production: true,
  version: packageData.version,
  /* Redirect API URL */
  apiUrl: 'https://localhost/redirect-api/redirect/',
  /* Act API URL */
  tmpActApi: 'https://localhost/act/',
  /* GraphQL API URL */
  graphqlApi: 'https://localhost:4001/graphql',
  /* Firewall API URL */
  firewallApi: 'https://localhost/firewall',
  /* Recommended system API URL */
  recommenderApi: 'http://127.0.0.1:16005/',
};
