import { MatSnackBar } from '@angular/material/snack-bar';
import { Injectable } from '@angular/core';

const SNACKBAR_DURATION = 2000;

@Injectable({
  providedIn: 'root',
})
export class MessagingService {
  constructor(private snackbar: MatSnackBar) {}

  showError(message: string) {
    this.snackbar.open(message, null, { duration: SNACKBAR_DURATION * 3, panelClass: ['text-center', 'error'] });
  }

  showSuccess(message: string) {
    this.snackbar.open(message, null, { duration: SNACKBAR_DURATION, panelClass: ['text-center', 'success'] });
  }
}
