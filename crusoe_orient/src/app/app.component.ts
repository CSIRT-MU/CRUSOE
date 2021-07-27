import { Component } from '@angular/core';

import { OAuthService } from 'angular-oauth2-oidc';
import { JwksValidationHandler } from 'angular-oauth2-oidc-jwks';
import { authConfig } from './authentication/auth.config';
import { Router } from '@angular/router';
import { Title } from '@angular/platform-browser';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  constructor(private oauthService: OAuthService, public router: Router, private titleService: Title) {
    this.configureWithNewConfigApi();
    this.titleService.setTitle(environment.applicationName);
  }

  private configureWithNewConfigApi() {
    this.oauthService.configure(authConfig);
    this.oauthService.setStorage(localStorage);
    this.oauthService.tokenValidationHandler = new JwksValidationHandler();
    this.oauthService
      .loadDiscoveryDocumentAndTryLogin()
      .then(() => {
        this.router.initialNavigation();
      })
      .catch((_) => {
        console.error('Error reaching OIDC provider.');
        // this.authService.disableOIDC();
        this.router.initialNavigation();
      });
  }
}
