import * as packageData from '../../package.json';

export const environment = {
  applicationName: 'CRUSOE Dashboard',
  production: true,
  version: packageData.version,
  /* Base url - former RedirectAPI url apiUrl*/
  baseUrl: 'http://localhost/',
  /* Flower API URL */
  flowerUrl: 'http://localhost:5555/',
  /* Act API URL */
  tmpActApi: 'http://localhost/act/',
  /* GraphQL API URL */
  graphqlApi: 'http://localhost:4001/graphql',
  /* Firewall API URL */
  firewallApi: 'http://localhost/firewall',
  /* Recommended system API URL */
  recommenderApi: 'http://127.0.0.1:16005/',
};
