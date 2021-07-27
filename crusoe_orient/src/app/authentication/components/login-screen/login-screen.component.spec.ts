import { RouterTestingModule } from '@angular/router/testing';
import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';
import { LoginScreenComponent } from './login-screen.component';
import { OAuthService } from 'angular-oauth2-oidc';
import { AuthService } from '../../services/auth.service';
import { By } from '@angular/platform-browser';
import { CommonModule } from '@angular/common';

describe('LoginScreenComponent', () => {
  let component: LoginScreenComponent;
  let fixture: ComponentFixture<LoginScreenComponent>;

  beforeEach(
    waitForAsync(() => {
      TestBed.configureTestingModule({
        imports: [RouterTestingModule.withRoutes([]), CommonModule],
        providers: [
          { provide: AuthService, useValue: jasmine.createSpyObj(['isOIDCenabled']) },
          { provide: OAuthService, useValue: jasmine.createSpyObj(['initImplicitFlow']) },
        ],
        declarations: [LoginScreenComponent],
      }).compileComponents();
    })
  );

  it('should create', () => {
    fixture = TestBed.createComponent(LoginScreenComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
    expect(component).toBeTruthy();
    const element = fixture.debugElement.nativeElement;
    document.body.removeChild(element);
  });

  it('should show oidc login button', () => {
    let authServiceMock;
    authServiceMock = TestBed.get(AuthService);
    authServiceMock.isOIDCenabled.and.returnValue(true);

    fixture = TestBed.createComponent(LoginScreenComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
    expect(authServiceMock.isOIDCenabled).toHaveBeenCalled();
    expect(component.showOIDCButton).toBeTrue();
    expect(fixture.debugElement.query(By.css('.alert.alert-warning'))).toBeNull();
    expect(fixture.debugElement.query(By.css('.oidc-login-button')).nativeElement).toBeTruthy();
  });

  it('should show warning instead of oidc login button', () => {
    let authServiceMock;
    authServiceMock = TestBed.inject(AuthService);
    authServiceMock.isOIDCenabled.and.returnValue(false);

    fixture = TestBed.createComponent(LoginScreenComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
    expect(authServiceMock.isOIDCenabled).toHaveBeenCalled();
    expect(component.showOIDCButton).toBeFalse();
    expect(fixture.debugElement.query(By.css('.alert.alert-warning')).nativeElement).toBeTruthy();
    expect(fixture.debugElement.query(By.css('.oidc-login-button'))).toBeNull();
  });
});
