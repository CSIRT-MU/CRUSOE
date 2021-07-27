import { Mission, Configuration } from './models/mission.model';
import { Component, OnInit, ViewChild, OnDestroy } from '@angular/core';
import { MatTable } from '@angular/material/table';
import { timer, Subscription, forkJoin, Observable, combineLatest, of } from 'rxjs';
import { Pao, PaoResponse } from './models/pao.model';
import { DecideService } from './decideact.service';
import { map, mergeMap, catchError, tap } from 'rxjs/operators';
import { MatSnackBar } from '@angular/material/snack-bar';
import { PaoStatus } from './models/pao-status.model';
import { Message } from './models/message.model';
import { FormControl, Validators } from '@angular/forms';
import { environment } from 'src/environments/environment';
import { MissionStructure } from './models/mission-structure.model';

@Component({
  selector: 'app-decide-act',
  templateUrl: './decideact.component.html',
  styleUrls: ['./decideact.component.scss'],
})
export class DecideActComponent implements OnInit, OnDestroy {
  paos: Pao[];
  title = 'Decide';
  paoColumns = ['name', 'status', 'capacity'];
  missions: Mission[];
  configColumns = ['check', 'name', 'integrity', 'confidentiality', 'availability'];
  feedbackLog: Message[] = [];
  contentLoading: boolean;
  securityThreshold = new FormControl('', [Validators.required, Validators.max(100)]);
  disableApply = true;
  feedbackLogSubscription: Subscription;
  missionsStructure: MissionStructure;
  errorMessage = '';
  firewallErrorMessage = '';
  firewallLoading: boolean;
  blockedIPs: string[] = [];
  applyLoading = false;

  @ViewChild(MatTable) table: MatTable<any>;

  constructor(private decide: DecideService, private snackbar: MatSnackBar) {}

  /**
   * Returns an observable of missions filled with configurations
   */
  private getMissions(): Observable<Mission[]> {
    let missions: Mission[] = [];
    return this.decide.getMissions().pipe(
      tap((ms: Mission[]) => {
        if (!this.missionsStructure) {
          this.missionsStructure = this.decide.makeMissionsStructure(ms);
        }
      }),
      mergeMap((ms: Mission[]) => {
        missions = [...ms];
        const configsObservable = missions.map((m) => {
          return this.decide.getMissionConfigurations(m.name);
        });
        if (configsObservable.length === 0) {
          return of([]);
        }
        return forkJoin(configsObservable);
      }),
      map((missionConfigs: Configuration[][]) => {
        missionConfigs.forEach((c: Configuration[], i: number) => {
          missions[i].configurations = c.sort(
            (c1: Configuration, c2: Configuration) => c1.configuration.config_id - c2.configuration.config_id
          );
        });
        return missions;
      })
    );
  }

  /**
   * Returns an observable containing paos filled with capacity and status
   */
  private getPaos(): Observable<Pao[]> {
    let paos: Pao[];
    return this.decide.getPaos().pipe(
      mergeMap((ps: PaoResponse) => {
        paos = ps.paos;
        const paosObservable = paos.map((p) => {
          return forkJoin(
            this.decide.getPaoUsedCapacity(p.pao).pipe(catchError((_) => of({ usedCapacity: 'Unknown' }))),
            this.decide.getPaoMaxCapacity(p.pao).pipe(catchError((_) => of({ maxCapacity: 'Unknown' }))),
            this.decide.getPaoStatus(p.pao).pipe(catchError((_) => of(null)))
          );
        });
        if (paosObservable.length === 0) {
          return of([]);
        }
        return forkJoin(paosObservable);
      }),
      map((paosInfo: [{ usedCapacity: number }, { maxCapacity: number }, PaoStatus][]) => {
        paosInfo.forEach((p, i) => {
          paos[i].usedCapacity = p[0]?.usedCapacity;
          paos[i].maxCapacity = p[1]?.maxCapacity;
          paos[i].status = p[2];
        });
        return paos;
      })
    );
  }

  /**
   * Returns an observable containing number (security threshold)
   */
  private getSecurityThreshold(): Observable<number> {
    return this.decide.getSecurityThreshold().pipe(map((r) => r.security_treshold));
  }

  ngOnInit(): void {
    // Feedback log
    const tmr = timer(0, 1500);
    this.feedbackLogSubscription = tmr.subscribe(() => {
      this.decide.getLogMessages().subscribe((messages: Message[]) => {
        this.feedbackLog = [];
        messages.forEach((m) => {
          this.appendMessage(m);
        });
      });
    });
    this.contentLoading = true;
    this.getData();
  }

  private getBlockedIPS() {
    this.firewallLoading = true;
    this.firewallErrorMessage = '';
    return this.decide.getBlockedIPS();
  }

  private getMissionData(): Observable<[Mission[], Pao[], number]> {
    this.errorMessage = '';
    return combineLatest(this.getMissions(), this.getPaos(), this.getSecurityThreshold());
  }

  private getData(): void {
    this.getMissionData().subscribe(
      ([missions, paos, securityThreshold]) => {
        this.missions = missions;
        this.paos = paos;

        this.securityThreshold.setValue(securityThreshold);
        this.contentLoading = false;
        this.applyLoading = false;
        this.checkConfigs();
      },
      (error) => {
        if (error.url === environment.firewallApi + '/blocked') {
          this.firewallErrorMessage = error.message;
        } else {
          this.errorMessage = error.message;
        }
        this.contentLoading = false;
        this.applyLoading = false;
        this.checkConfigs();
      }
    );

    this.getBlockedIPS().subscribe(
      (result) => {
        this.blockedIPs = result.map((ip) => ip.ip);
        this.firewallLoading = false;
      },
      (error) => {
        this.firewallErrorMessage = error.message;
        this.firewallLoading = false;
      }
    );
  }

  showPaoStatus(status: PaoStatus): string {
    if (
      !status ||
      status.status_green === undefined ||
      status.status_red === undefined ||
      status.status_yellow === undefined
    ) {
      return 'Not available.';
    }

    if (status.status_red !== '') {
      let messages = status.status_red.split(',');
      messages = messages.map((message) => `<span>${message}</span>`);
      return `<p class="pao-status red">${messages.join('')}</p>`;
    }

    if (status.status_yellow !== '') {
      let messages = status.status_yellow.split(',');
      messages = messages.map((message) => `<span>${message}</span>`);
      return `<p class="pao-status yellow">${messages.join('')}</p>`;
    }

    if (status.status_green !== '') {
      let messages = status.status_green.split(',');
      messages = messages.map((message) => `<span>${message}</span>`);
      return `<p class="pao-status green">${messages.join('')}</p>`;
    }
  }

  /**
   * Returns name of the mission's selected config
   * @param mission
   */
  selectedConfig(mission: Mission): string {
    if (mission.selectedConfig) {
      return 'Config ' + mission.selectedConfig?.configuration.config_id.toString();
    }
    return 'No config';
  }

  appendMessage(message: Message) {
    this.feedbackLog.push(message);
  }

  /**
   * Selects/Unselects config of a mission
   * @param mission
   * @param config
   */
  toggleConfig(mission: Mission, config: Configuration) {
    if (config.selected) {
      config.selected = false;
      mission.selectedConfig = null;
    } else {
      if (mission.selectedConfig) {
        mission.selectedConfig.selected = false;
      }
      config.selected = true;
      mission.selectedConfig = config;
    }

    this.checkConfigs();
  }

  /**
   * Checks if for every mission there is a config selected
   */
  private checkConfigs() {
    if (this.missions.filter((m: Mission) => !m.selectedConfig).length === 0) {
      this.disableApply = false;
    } else {
      this.disableApply = true;
    }
  }

  /**
   * Update security threshold
   */
  updateThreshold(threshold: number) {
    this.decide.setSecurityThreshold(threshold).subscribe(
      (response: string) => {
        this.snackbar.open(response, '', { duration: 3000 });
      },
      (error) => {
        this.snackbar.open(error.message, '', { duration: 3000, panelClass: ['text-center', 'error'] });
      }
    );
  }

  /**
   * Apply mission configs
   */
  applyConfigs() {
    if (this.applyLoading) {
      return;
    }

    this.applyLoading = true;
    this.firewallLoading = true;
    const configs: { name: string; config_id: number }[] = [];
    this.missions.forEach((m: Mission) => {
      configs.push({ name: m.name, config_id: m.selectedConfig.configuration.config_id });
      m.selectedConfig = null;
    });

    this.decide.applyMissionConfig(configs).subscribe(
      (message: string) => {
        this.getData();
        this.snackbar.open(message, '', { duration: 3000 });
      },
      (error) => {
        this.snackbar.open(error.message, '', { duration: 5000, panelClass: ['text-center', 'error'] });
        this.applyLoading = false;
        this.firewallLoading = false;
        this.checkConfigs();
      }
    );
  }

  ngOnDestroy(): void {
    this.feedbackLogSubscription.unsubscribe();
  }
}
