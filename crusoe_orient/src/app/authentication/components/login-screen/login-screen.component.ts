import { AuthService } from '../../services/auth.service';
import { Component, OnInit, ViewChild, ElementRef, Renderer2 } from '@angular/core';

import { OAuthService } from 'angular-oauth2-oidc';
import { environment } from 'src/environments/environment';

/**
 * Component with login form and submit callback.
 */
@Component({
  selector: 'app-login',
  templateUrl: './login-screen.component.html',
  styleUrls: ['./login-screen.component.scss'],
})
export class LoginScreenComponent implements OnInit {
  lastErrorMessage = '';
  showOIDCButton = true;
  @ViewChild('localLoginElem') localLoginElem: ElementRef<HTMLElement>;
  @ViewChild('oidcLoginElem') oidcLoginElem: ElementRef<HTMLElement>;
  appVersion: string = environment.version;
  appName = environment.applicationName;

  constructor(private oauthService: OAuthService, private authService: AuthService, private renderer: Renderer2) {
    this.showOIDCButton = this.authService.isOIDCenabled();
  }

  ngOnInit() {
    // this.lastErrorMessage = this.authService.getLastError();
  }

  oidcLogin() {
    this.oauthService.initImplicitFlow();
  }
}
