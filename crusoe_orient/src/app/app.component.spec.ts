import { HttpClientModule } from '@angular/common/http';
import { TestBed, waitForAsync } from '@angular/core/testing';
import { AppComponent } from './app.component';

import { environment } from 'src/environments/environment';
import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { OAuthModule } from 'angular-oauth2-oidc';
import { RouterTestingModule } from '@angular/router/testing';

describe('AppComponent', () => {
  beforeEach(
    waitForAsync(() => {
      TestBed.configureTestingModule({
        declarations: [AppComponent],
        imports: [
          OAuthModule.forRoot({
            resourceServer: {
              allowedUrls: ['https://oidc.muni.cz/oidc/userinfo', 'http://localhost:8000/api/panels'],
              sendAccessToken: true,
            },
          }),
          HttpClientModule,
          RouterTestingModule.withRoutes([]),
        ],
        schemas: [CUSTOM_ELEMENTS_SCHEMA],
      }).compileComponents();
    })
  );
  it(
    'should create the app',
    waitForAsync(() => {
      const fixture = TestBed.createComponent(AppComponent);
      const app = fixture.debugElement.componentInstance;
      expect(app).toBeTruthy();
    })
  );
  it(
    `should have title ${environment.applicationName}`,
    waitForAsync(() => {
      const fixture = TestBed.createComponent(AppComponent);
      const title = fixture.debugElement.componentInstance.titleService.getTitle();
      expect(title).toEqual(environment.applicationName);
    })
  );
});
