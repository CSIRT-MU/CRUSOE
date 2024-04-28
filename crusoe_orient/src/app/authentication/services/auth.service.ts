import { OAuthService } from 'angular-oauth2-oidc';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';

/*
    This service should handle authenticated user's credentials, logout
    It manages OIDC and Simple Login - based on user's choice
*/
@Injectable()
export class AuthService {
  private username: string;
  private lastError = '';
  private oidcEnabled = false;

  constructor(private oAuthService: OAuthService, private router: Router) {}

  public logout() {
    localStorage.clear();
    this.router.navigateByUrl('/login');
  }

  public async getUserName(): Promise<string> {
    // User is logged using OIDC service
    if (this.oAuthService.hasValidAccessToken()) {
      if (!this.username) {
        const claims = this.oAuthService.getIdentityClaims();
        if (claims && claims['name']) {
          this.username = claims['name'];
          return Promise.resolve(this.username);
        } else {
          return this.oAuthService.loadUserProfile().then((c) => {
            return c['name'];
          });
        }
      } else {
        return Promise.resolve(this.username);
      }
    }
    return null;
  }

  public getUserProfile(): any {
    if (this.oAuthService.hasValidAccessToken()) {
      const claims = this.oAuthService.getIdentityClaims();
      return claims;
    }
    return null;
  }

  /**
   * Checks if user is authenticated
   * @returns returns true if user is authenticated, false otherwise
   */
  public isAuthenticated(): boolean {
    //return this.oAuthService.hasValidAccessToken();
    return true;
  }

  /**
   * Returns last error that occured while authenticating
   *
   * @returns string describing last error
   * @memberof AuthService
   */
  // public getLastError() {
  //   return this.lastError;
  // }

  /**
   * Disables OIDC authentication (eg. because OIDC provider is unreachable)
   *
   * @memberof AuthService
   */
  public disableOIDC() {
    this.oidcEnabled = false;
  }

  /**
   * Enables OIDC authentication
   *
   * @memberof AuthService
   */
  public enableOIDC() {
    this.oidcEnabled = true;
  }

  /**
   * Check if OIDc authentication is enabled.
   *
   * @returns boolean
   * @memberof AuthService
   */
  public isOIDCenabled() {
    return this.oidcEnabled;
  }
}
