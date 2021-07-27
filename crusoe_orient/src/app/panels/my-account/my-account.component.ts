import { Component, OnInit } from '@angular/core';
import { AuthService } from 'src/app/authentication/services/auth.service';

/**
 * Displays user profile with details and settings.
 */
@Component({
  selector: 'app-my-account',
  templateUrl: './my-account.component.html',
  styleUrls: ['./my-account.component.scss'],
})
export class MyAccountComponent implements OnInit {
  constructor(private auth: AuthService) {}
  /**
   * Function to be called on component initialisation.
   */
  ngOnInit() {}

  get userProfile() {
    return this.auth.getUserProfile();
  }
}
