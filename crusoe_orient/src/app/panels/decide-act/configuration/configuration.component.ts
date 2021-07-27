import { Component, OnInit } from '@angular/core';
import { Configuration, Mission } from '../models/mission.model';
import { ActivatedRoute } from '@angular/router';
import { DecideService } from '../decideact.service';
import { zip } from 'rxjs';
import { Host } from '../models/hosts.model';
import { MissionStructure } from '../models/mission-structure.model';
import { map } from 'rxjs/operators';

@Component({
  selector: 'app-configuration',
  templateUrl: './configuration.component.html',
  styleUrls: ['./configuration.component.scss'],
})
export class ConfigurationComponent implements OnInit {
  configuration: Configuration;
  configLoading: boolean;
  hosts: Host[];
  hostsArray: string[];
  hostsString: string;
  missionName: string;
  missionsStructure: MissionStructure;
  missionGraphLoading: boolean;
  errorMessage = '';

  constructor(private route: ActivatedRoute, private decide: DecideService) {}

  ngOnInit(): void {
    this.configLoading = true;
    this.missionGraphLoading = true;

    if (this.route.snapshot.params) {
      this.missionName = this.route.snapshot.params.missionName;
      const configId = Number(this.route.snapshot.params.id);

      const $getConfig = this.decide.getMissionConfiguration(this.missionName, configId);
      const $getHosts = this.decide.getConfigurationHosts(this.missionName, configId);
      const $getStructure = this.decide.getMission(this.missionName).pipe(map((m) => m.structure));

      zip($getConfig, $getHosts, $getStructure, (config: Configuration, hosts: Host[], structure: string) => ({
        config,
        hosts,
        structure,
      })).subscribe(
        (response) => {
          this.configuration = response.config;
          this.hosts = response.hosts;
          if (Array.isArray(this.hosts)) {
            this.hostsArray = this.hosts.map((h) => h.host.hostname);
            this.hostsString = this.hostsArray.join(', ');
          }
          this.configLoading = false;
          console.log(response.structure);
          this.missionsStructure = JSON.parse(response.structure);
          this.missionGraphLoading = false;
        },
        (error) => {
          this.errorMessage = error.message;
          this.configLoading = false;
          this.missionGraphLoading = false;
        }
      );
    }
  }
}
