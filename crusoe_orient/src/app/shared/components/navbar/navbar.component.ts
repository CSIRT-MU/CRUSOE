import { AuthService } from '../../../authentication/services/auth.service';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss'],
})
export class NavbarComponent implements OnInit {
  userProfileLoaded = false;
  userName: Promise<string>;

  constructor(private authService: AuthService) {
    this.userName = this.authService.getUserName();
  }

  ngOnInit() {}

  logout() {
    this.authService.logout();
  }
}
