import { Component, OnInit, ViewChild, ElementRef, AfterViewInit, Input } from '@angular/core';
import { Panel } from 'src/app/shared/models/general-panel.model';
import { PanelGroup } from 'src/app/shared/models/panel_group.model';
import { environment } from 'src/environments/environment';
import { panels, panelGroups } from 'src/app/app-routing.module';
import { AuthService } from 'src/app/authentication/services/auth.service';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['sidebar.component.scss'],
})
export class SidebarComponent implements OnInit, AfterViewInit {
  panels: Panel[];
  panelGroups: PanelGroup[];
  appVersion = environment.version;
  appName = environment.applicationName;

  constructor(private auth: AuthService) {
    this.panels = panels.map(({ data: { name, panelGroup }, path }) => ({ name, path, panelGroup }));
    this.panelGroups = panelGroups;
  }

  ngAfterViewInit() {}

  ngOnInit() {}
}
