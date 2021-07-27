import { Injectable } from '@angular/core';
import { HttpRequest, HttpHandler, HttpEvent, HttpInterceptor } from '@angular/common/http';
import { Observable } from 'rxjs';
import { OAuthService } from 'angular-oauth2-oidc';
import { environment } from 'src/environments/environment';

@Injectable()
export class ApiInterceptor implements HttpInterceptor {
  constructor(private oauthService: OAuthService) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    // Check if request is going to Redirect-API URL, if so add oidc access_token
    if (req.url.indexOf(environment.apiUrl) > -1 || req.url.indexOf(environment.graphqlApi) > -1) {
      const access_token = this.oauthService.getAccessToken();
      const authHeader = `Bearer ${access_token}`;

      const newReq = req.clone({
        setHeaders: {
          Authorization: authHeader,
        },
      });
      return next.handle(newReq);
    }
    return next.handle(req);
  }
}
