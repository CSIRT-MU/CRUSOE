import { AuthService } from './auth.service';

describe('AuthService', () => {
  let authService: AuthService;
  let router;
  let oAuthServiceMock;

  beforeEach(() => {
    oAuthServiceMock = jasmine.createSpyObj('OAuthService', [
      'hasValidAccessToken',
      'getIdentityClaims',
      'loadUserProfile',
    ]);
    router = jasmine.createSpyObj('Router', ['navigateByUrl']);
    authService = new AuthService(oAuthServiceMock, router);

    let fakeLocalStorage = {};

    spyOn(localStorage, 'getItem').and.callFake(function (key) {
      return fakeLocalStorage[key];
    });
    spyOn(localStorage, 'setItem').and.callFake(function (key, value) {
      return (fakeLocalStorage[key] = value + '');
    });
    spyOn(localStorage, 'clear').and.callFake(function () {
      fakeLocalStorage = {};
    });
  });

  it('should get and store username from oidc store', async () => {
    oAuthServiceMock.hasValidAccessToken.and.returnValue(true);
    oAuthServiceMock.getIdentityClaims.and.returnValue({ name: 'Lukas' });

    let username = await authService.getUserName();
    expect(oAuthServiceMock.hasValidAccessToken).toHaveBeenCalledTimes(1);
    expect(oAuthServiceMock.getIdentityClaims).toHaveBeenCalledTimes(1);
    expect(username).toEqual('Lukas');

    oAuthServiceMock.getIdentityClaims.and.returnValue({ name: 'NotLukas' });
    username = await authService.getUserName();
    expect(username).toEqual('Lukas');
  });

  it('should get and store username from oidc server', async () => {
    let username: string;
    oAuthServiceMock.hasValidAccessToken.and.returnValue(true);
    oAuthServiceMock.getIdentityClaims.and.returnValue(null);
    oAuthServiceMock.loadUserProfile.and.returnValue(
      new Promise(function (resolve, _) {
        resolve({ name: 'Johny' });
      })
    );

    username = await authService.getUserName();
    expect(oAuthServiceMock.loadUserProfile).toHaveBeenCalled();
    expect(username).toEqual('Johny');
  });

  it('should return null for username if token is not valid', async () => {
    let username: string;
    oAuthServiceMock.hasValidAccessToken.and.returnValue(false);

    username = await authService.getUserName();
    expect(username).toBeNull();
  });

  it('should return identity claims', async () => {
    let claims: any;

    oAuthServiceMock.hasValidAccessToken.and.returnValue(false);
    claims = authService.getUserProfile();
    expect(claims).toBeNull();

    oAuthServiceMock.hasValidAccessToken.and.returnValue(true);
    oAuthServiceMock.getIdentityClaims.and.returnValue({ name: 'Lukas', age: 25 });

    claims = authService.getUserProfile();
    expect(claims.name).toEqual('Lukas');
    expect(claims.age).toEqual(25);
  });

  it('should clear local storage and redirect on logout', () => {
    localStorage.setItem('user', 'Lukas');
    expect(localStorage.getItem('user')).toEqual('Lukas');
    expect(router.navigateByUrl).not.toHaveBeenCalled();
    authService.logout();
    expect(router.navigateByUrl).toHaveBeenCalledWith('/login');
    expect(localStorage.getItem('user')).toBeUndefined();
  });

  it('should return isAuthenticated based on valid access token', () => {
    oAuthServiceMock.hasValidAccessToken.and.returnValue(false);
    expect(authService.isAuthenticated()).toEqual(false);
    oAuthServiceMock.hasValidAccessToken.and.returnValue(true);
    expect(authService.isAuthenticated()).toEqual(true);
  });

  it('should enable and disable OIDC and show last error', () => {
    let enabled = authService.isOIDCenabled();
    expect(enabled).toBeTrue();
    authService.disableOIDC();
    enabled = authService.isOIDCenabled();
    expect(enabled).toBeFalse();
    authService.enableOIDC();
    enabled = authService.isOIDCenabled();
    expect(enabled).toBeTrue();
  });
});
