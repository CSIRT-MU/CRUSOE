import { Title } from '@angular/platform-browser';
import { Component, OnInit } from '@angular/core';
import { environment } from 'src/environments/environment';
import { AuthService } from 'src/app/authentication/services/auth.service';
import { ActivatedRoute } from '@angular/router';
import { panelsText } from '../../app-routing.module';

@Component({
  selector: 'app-panel-overview',
  templateUrl: './panel-overview.component.html',
  styleUrls: ['./panel-overview.component.scss'],
})
export class PanelOverviewComponent implements OnInit {
  panels: any;

  constructor(private titleService: Title, private auth: AuthService, private route: ActivatedRoute) {
    this.panels = route.snapshot.data.panelsText;
    this.titleService.setTitle('Overview - ' + environment.applicationName + ' by CSIRT-MU');
  }

  ngOnInit() {}
}
