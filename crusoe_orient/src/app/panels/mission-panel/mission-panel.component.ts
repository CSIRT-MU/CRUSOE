import { Component, OnInit } from '@angular/core';
import { DataService } from '../../shared/services/data.service';
import { Mission } from '../decide-act/models/mission.model';
import { MissionStructure } from '../decide-act/models/mission-structure.model';
import { tap } from 'rxjs/operators';
import { Observable } from 'rxjs';

@Component({
  selector: 'mission-panel',
  templateUrl: './mission-panel.component.html',
  styleUrls: ['./mission-panel.component.scss'],
})
export class MissionPanelComponent implements OnInit {
  errorMessage = '';
  missionNames: string[] = [];
  selectedMission = "";
  missions: Mission[] = [];
  missionsStructure: MissionStructure;

  constructor(private dataService: DataService) {
  }

  ngOnInit(): void {
    this.dataService.getMissionNames().subscribe(
      (missionNames) => {
        this.missionNames = missionNames;
      },
      (error) => {
        this.errorMessage = error.message || 'Error fetching subnets'; // Handle errors
      }
    );
    this.getGraphData();
  }

  public getGraphData(): void {
    this.getMissions().subscribe(
      (missions) => {
        this.missions = missions;
        this.missionsStructure = this.dataService.makeMissionsStructure(missions);
      }
    );
  }

  /**
   * Returns an observable of missions
   */
  private getMissions(): Observable<Mission[]> {
    return this.dataService.getMission(this.selectedMission).pipe(
      tap((missions: Mission[]) => {
        if (!this.missionsStructure) {
          this.missionsStructure = this.dataService.makeMissionsStructure(missions);
        }
      })
    );
  }
}
