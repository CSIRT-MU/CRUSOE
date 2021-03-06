import { Observable } from 'rxjs';
import { AuthService } from './auth.service';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router, UrlTree } from '@angular/router';
import { Injectable } from '@angular/core';

/**
 * Guard to protect routes against guest users.
 */
@Injectable()
export class AuthGuard implements CanActivate {
  /**
   * Constructor with DI
   * @param auth Injected AuthService
   * @param router Injected Router for redirection
   */
  constructor(private router: Router, private authService: AuthService) {}

  /**
   * Implements function telling if route can be activated or not.
   * @param route Activated route
   * @param state Router state
   */
  canActivate(
    next: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): Observable<boolean> | Promise<boolean> | boolean | UrlTree {
    if (!this.authService.isAuthenticated()) {
      return this.router.parseUrl('/login');
    } else {
      return true;
    }
  }
}
