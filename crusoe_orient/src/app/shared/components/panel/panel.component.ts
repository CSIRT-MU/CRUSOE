import { Panel } from 'src/app/shared/models/general-panel.model';
import { Component, OnInit, OnDestroy } from '@angular/core';
import { Title } from '@angular/platform-browser';
import { environment } from 'src/environments/environment';
import { ActivatedRoute, Router, NavigationEnd } from '@angular/router';
import { Subscription } from 'rxjs';
import { trigger, transition, query, style, animate } from '@angular/animations';

@Component({
  selector: 'app-panel',
  templateUrl: './panel.component.html',
  styleUrls: ['./panel.component.scss'],
  animations: [
    trigger('fadeAnimation', [
      transition('* => *', [
        query(
          ':enter, :leave',
          [
            style({
              position: 'absolute',
              width: '100%',
              left: 0,
              top: 0,
            }),
          ],
          { optional: true }
        ),
        query(':enter', [style({ opacity: 0 })], { optional: true }),
        query(':leave', [style({ opacity: 1 }), animate('0.2s', style({ opacity: 0 }))], { optional: true }),
        query(':enter', [style({ opacity: 0 }), animate('0.2s', style({ opacity: 1 }))], { optional: true }),
      ]),
    ]),
  ],
})
export class PanelComponent implements OnInit, OnDestroy {
  panel: Panel;
  sub: Subscription;
  name: string;
  type: string;

  constructor(private titleService: Title, private route: ActivatedRoute, private router: Router) {
    this.sub = this.route.url.subscribe(() => {
      this.name = route.snapshot.firstChild.data.name || route.snapshot.firstChild.params.name;
      this.type = route.snapshot.firstChild.data.type;

      if (!this.name) {
        this.name = route.snapshot.firstChild.paramMap.get('id');
      }

      if (route.snapshot.firstChild.params.missionName) {
        this.name = route.snapshot.firstChild.params.missionName + ' / ' + route.snapshot.firstChild.params.id;
      }

      this.titleService.setTitle(this.name + ' - ' + environment.applicationName);
    });
  }

  ngOnInit() {
    this.router.events.subscribe((evt) => {
      if (!(evt instanceof NavigationEnd)) {
        return;
      }
      window.scrollTo(0, 0);
    });
  }

  ngOnDestroy() {
    this.sub.unsubscribe();
  }

  public getRouterOutletState(outlet) {
    return outlet.isActivated ? outlet.activatedRoute : '';
  }
}
