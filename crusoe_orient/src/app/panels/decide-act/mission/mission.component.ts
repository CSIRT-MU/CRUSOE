import { Component, OnInit, Input } from '@angular/core';
import { DecideService } from '../decideact.service';
import { Mission } from '../models/mission.model';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-mission',
  templateUrl: './mission.component.html',
  styleUrls: ['./mission.component.scss'],
})
export class MissionComponent implements OnInit {
  mission: Mission;
  missionLoading = true;
  errorMessage = '';

  constructor(private route: ActivatedRoute, private decide: DecideService) {}

  ngOnInit(): void {
    const name = this.route.snapshot.params.name;
    this.decide.getMission(name).subscribe(
      (mission: Mission) => {
        this.mission = mission;
        this.missionLoading = false;
      },
      (error) => {
        this.missionLoading = false;
        this.errorMessage = error.message;
      }
    );
  }
}
