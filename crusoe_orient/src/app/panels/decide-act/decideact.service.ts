import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { Observable } from 'rxjs';
import { PaoResponse } from './models/pao.model';
import { Mission, Configuration } from './models/mission.model';
import { PaoStatus } from './models/pao-status.model';
import { Message } from './models/message.model';
import { map } from 'rxjs/operators';
import { Host } from './models/hosts.model';
import { BlockedIP } from './models/blocked-ip.model';
import { MissionStructure, Relationships } from './models/mission-structure.model';

@Injectable({
  providedIn: 'root',
})
export class DecideService {
  constructor(private http: HttpClient) {}

  /**
   * Get list of PAOS
   */
  public getPaos(): Observable<PaoResponse> {
    return this.http.get<PaoResponse>(environment.apiUrl + 'rest/' + 'act/paos');
  }

  /**
   * Get names of the missions
   * I suggested to modify API endpoint used here - https://gitlab.ics.muni.cz/CRUSOE/neo4j-rest/-/issues/9
   */
  public getMissions(): Observable<Mission[]> {
    return this.http.get<Mission[]>(environment.apiUrl + 'rest/' + 'missions');
  }

  /**
   * Get mission configurations
   */
  public getMissionConfigurations(mission: string): Observable<Configuration[]> {
    return this.http.get<Configuration[]>(environment.apiUrl + 'rest/' + 'mission/' + mission + '/configurations');
  }

  /**
   * Get specific configuration of given mission
   * @param mission Name of the mission
   * @param id Id of the configuration
   */
  public getMissionConfiguration(mission: string, id: number): Observable<Configuration> {
    return this.http.get<Configuration[]>(environment.apiUrl + 'rest/' + 'mission/' + mission + '/configurations').pipe(
      map((configs) => {
        const configsFiltered = configs.filter((c) => {
          return c.configuration.config_id === id;
        });
        return configsFiltered[0];
      })
    );
  }

  /**
   * Gets structure parameter from each mission and merges them into one structure
   * @param ms list of missions
   *
   */
  public makeMissionsStructure(ms: Mission[]): MissionStructure {
    let result: MissionStructure;
    let structure: MissionStructure;

    result = ms.reduce(
      (acc, mission) => {
        structure = JSON.parse(mission.structure);
        return {
          nodes: {
            missions: [...acc.nodes.missions, ...structure.nodes.missions],
            hosts: [...acc.nodes.hosts, ...structure.nodes.hosts],
            services: [...acc.nodes.services, ...structure.nodes.services],
            aggregations: {
              or: [...acc.nodes.aggregations.or, ...structure.nodes.aggregations.or],
              and: [...acc.nodes.aggregations.and, ...structure.nodes.aggregations.and],
            },
          },
          relationships: {
            two_way: [...acc.relationships.two_way, ...structure.relationships.two_way],
            one_way: [...acc.relationships.one_way, ...structure.relationships.one_way],
            supports: [...acc.relationships.supports, ...structure.relationships.supports],
            has_identity: [...acc.relationships.has_identity, ...structure.relationships.has_identity],
          },
        };
      },
      {
        nodes: { missions: [], hosts: [], aggregations: { and: [], or: [] }, services: [] },
        relationships: { two_way: [], one_way: [], supports: [], has_identity: [] },
      }
    );

    return result;
  }

  /**
   * Get hosts affected by given configuration
   * @param mission Name of the mission
   * @param id Id of the configuration
   */
  public getConfigurationHosts(mission: string, id: number): Observable<Host[]> {
    return this.http.get<Host[]>(
      environment.apiUrl + 'rest/' + 'mission/' + mission + '/configuration/' + id + '/hosts'
    );
  }

  /** Get PAO maximum capacity */
  public getPaoMaxCapacity(pao: string): Observable<{ maxCapacity: number }> {
    return this.http.get<{ maxCapacity: number }>(environment.apiUrl + 'rest/' + 'act/' + pao + '/maxCapacity');
  }

  /** Get PAO used capacity */
  public getPaoUsedCapacity(pao: string): Observable<{ usedCapacity: number }> {
    return this.http.get<{ usedCapacity: number }>(environment.apiUrl + 'rest/' + 'act/' + pao + '/usedCapacity');
  }

  /**
   * Get status of the PAO
   */
  public getPaoStatus(pao: string): Observable<PaoStatus> {
    return this.http.get<PaoStatus>(environment.apiUrl + 'rest/' + 'act/' + pao + '/status');
  }

  /**
   * Get security threshold
   */
  public getSecurityThreshold(): Observable<{ security_treshold: number }> {
    return this.http.get<{ security_treshold: number }>(environment.tmpActApi + 'treshold');
  }

  /**
   * Update security threshold
   */
  public setSecurityThreshold(threshold: number): Observable<string> {
    const body = {
      security_treshold: threshold,
    };

    return this.http.put<string>(environment.tmpActApi + 'treshold', body, {
      headers: { 'Content-Type': 'application/json' },
    });
  }

  /**
   * Apply mission configs
   */
  public applyMissionConfig(config: { name: string; config_id: number }[]) {
    return this.http.post<string>(environment.tmpActApi + 'protect_missions_assets', config, {
      headers: { 'Content-Type': 'application/json' },
    });
  }

  /**
   * Get messages from log endpoint
   */
  public getLogMessages(): Observable<Message[]> {
    return this.http.get<Message[]>(environment.tmpActApi + 'log');
  }

  /**
   * Gets mission info
   * @param missionName
   */
  public getMission(missionName: string): Observable<Mission> {
    return this.http.get<Mission>(environment.apiUrl + 'rest/' + 'missions/' + missionName);
  }

  /**
   * Get structure of missions usable for graph
   */
  public getMissionsStructure(): Observable<any> {
    return this.getMissions().pipe(
      map((missions: Mission[]) => {
        const resultArray: string[] = missions.reduce((acc, currentMission) => [...acc, currentMission.structure], []);
        console.log('structures:', resultArray);
        return resultArray;
      })
    );
  }

  /**
   * Gets array of IPs currently blocked by firewall
   */
  public getBlockedIPS(): Observable<BlockedIP[]> {
    return this.http.get<BlockedIP[]>(environment.firewallApi + '/blocked');
  }
}
