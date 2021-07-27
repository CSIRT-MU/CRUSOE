import { AuthService } from '../../services/auth.service';
import { LogoutComponent } from './logout.component';

describe('LogoutComponent', () => {
  let authService: AuthService;
  let component: LogoutComponent;
  beforeAll(() => {
    authService = jasmine.createSpyObj('AuthService', ['logout']);
    component = new LogoutComponent(authService);
  });

  it('logout function on authService should be called', () => {
    console.log(authService);
    expect(authService.logout).not.toHaveBeenCalled();
    component.logout();
    expect(authService.logout).toHaveBeenCalled();
  });
});
