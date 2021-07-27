import { animate, state, style, transition, trigger } from '@angular/animations';
import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';

@Component({
  selector: 'app-auth-section',
  templateUrl: './auth-section.component.html',
  styleUrls: ['./auth-section.component.scss'],
  animations: [
    trigger('slideInOut', [
      state(
        'in',
        style({
          left: '0',
        })
      ),
      state(
        'out',
        style({
          left: '-300px',
        })
      ),
      transition('in => out', animate('200ms ease-out')),
      transition('out => in', animate('200ms ease-out')),
    ]),
  ],
})
export class AuthSectionComponent implements OnInit {
  sidebarState = 'in';
  @ViewChild('mainWrapper', { static: true }) mainWrapper: ElementRef;

  constructor() {}

  ngOnInit() {}

  toggleSidebar() {
    this.mainWrapper.nativeElement.classList.toggle('pl-0');
    this.mainWrapper.nativeElement.classList.toggle('pl-250px');
    this.sidebarState = this.sidebarState === 'out' ? 'in' : 'out';
  }

  onAnimationEvent(element: any) {
    window.dispatchEvent(new Event('resize'));
  }
}
