import { AuthConfig } from 'angular-oauth2-oidc';

let projectAddress = window.location.origin;

if (projectAddress === 'https://crusoe.csirt.muni.cz') {
  projectAddress = projectAddress + '/dashboard';
}

export const authConfig: AuthConfig = {
  // Url of the Identity Provider
  issuer: 'https://oidc.muni.cz/oidc/',

  // URL of the SPA to redirect the user after silent refresh
  silentRefreshRedirectUri: projectAddress + '/silent-refresh.html',

  // URL of the SPA to redirect the user to after login
  redirectUri: projectAddress + '/index.html',

  // The SPA's id. The SPA is registerd with this id at the auth-server
  clientId: 'fc603709-7735-4fdb-a0b0-ce19122c949b',

  // set the scope for the permissions the client should request
  // The first three are defined by OIDC. The 4th is a usecase-specific one
  scope: 'openid profile email eduperson_entitlement',

  sessionChecksEnabled: false,

  userinfoEndpoint: 'https://oidc.muni.cz/oidc/userinfo',
};
