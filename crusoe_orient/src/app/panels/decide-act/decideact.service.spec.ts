import { TestBed } from '@angular/core/testing';

import { DecideService } from './decideact.service';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { environment } from '../../../environments/environment.prod';

describe('DecideService', () => {
  let service: DecideService;
  let httpClientSpy: { get: jasmine.Spy; post: jasmine.Spy; put: jasmine.Spy };

  beforeEach(() => {
    httpClientSpy = jasmine.createSpyObj('HttpClient', ['get', 'post', 'put']);
    service = new DecideService(httpClientSpy as any);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should call http endpoint', () => {
    service.getPaos();
    expect(httpClientSpy.get).toHaveBeenCalledOnceWith(environment.apiUrl + 'rest/' + 'act/paos');

    service.getMissions();
    expect(httpClientSpy.get).toHaveBeenCalledWith(environment.apiUrl + 'rest/' + 'missions');

    service.getMissionConfigurations('5');
    expect(httpClientSpy.get).toHaveBeenCalledWith(environment.apiUrl + 'rest/' + 'mission/' + '5' + '/configurations');

    service.getConfigurationHosts('test', 2);
    expect(httpClientSpy.get).toHaveBeenCalledWith(
      environment.apiUrl + 'rest/' + 'mission/' + 'test' + '/configuration/' + 2 + '/hosts'
    );

    service.getPaoMaxCapacity('test');
    expect(httpClientSpy.get).toHaveBeenCalledWith(environment.apiUrl + 'rest/' + 'act/' + 'test' + '/maxCapacity');

    service.getPaoUsedCapacity('test');
    expect(httpClientSpy.get).toHaveBeenCalledWith(environment.apiUrl + 'rest/' + 'act/' + 'test' + '/usedCapacity');

    service.getPaoStatus('test');
    expect(httpClientSpy.get).toHaveBeenCalledWith(environment.apiUrl + 'rest/' + 'act/' + 'test' + '/status');

    service.getSecurityThreshold();
    expect(httpClientSpy.get).toHaveBeenCalledWith(environment.tmpActApi + 'treshold');

    service.setSecurityThreshold(5);
    expect(httpClientSpy.put).toHaveBeenCalledWith(
      environment.tmpActApi + 'treshold',
      {
        security_treshold: 5,
      },
      {
        headers: { 'Content-Type': 'application/json' },
      }
    );

    service.applyMissionConfig([{ name: 'test', config_id: 5 }]);
    expect(httpClientSpy.post).toHaveBeenCalledWith(
      environment.tmpActApi + 'protect_missions_assets',
      [{ name: 'test', config_id: 5 }],
      {
        headers: { 'Content-Type': 'application/json' },
      }
    );

    service.getLogMessages();
    expect(httpClientSpy.get).toHaveBeenCalledWith(environment.tmpActApi + 'log');

    service.getMission('test');
    expect(httpClientSpy.get).toHaveBeenCalledWith(environment.apiUrl + 'rest/' + 'missions/' + 'test');

    service.getBlockedIPS();
    expect(httpClientSpy.get).toHaveBeenCalledWith(environment.firewallApi + '/blocked');
  });
});
