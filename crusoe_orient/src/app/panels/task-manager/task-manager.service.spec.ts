import { TaskManagerService } from './task-manager.service';
import { of } from 'rxjs';

describe('TaskManagerService', () => {
  let httpClientSpy: { get: jasmine.Spy };
  let taskManagerService: TaskManagerService;

  beforeEach(() => {
    httpClientSpy = jasmine.createSpyObj('HttpClient', ['get']);
    taskManagerService = new TaskManagerService(httpClientSpy as any);
  });

  it('should get expected data from flower/dashboard', () => {
    const expectedData = {
      data: [
        {
          'worker-heartbeat': 949332,
          'worker-offline': 2,
          'worker-online': 2,
          'task-received': 52247,
          'task-started': 52247,
          'task-succeeded': 51473,
          'task-failed': 322,
          'task-retried': 449,
          hostname: 'celery@crusoe',
          pid: 22466,
          freq: 2,
          heartbeats: [1597394107.3317168, 1597394107.3337114, 1597394107.833331, 1597394109.8353212],
          clock: 1088819,
          active: 3,
          processed: 23482,
          loadavg: [1.77, 1.41, 1.02],
          sw_ident: 'py-celery',
          sw_ver: '4.4.6',
          sw_sys: 'Linux',
          status: true,
        },
      ],
    };
    httpClientSpy.get.and.returnValue(of(expectedData));

    taskManagerService.getDashboard().subscribe((data) => expect(data).toEqual(expectedData, 'expected heroes'), fail);

    expect(httpClientSpy.get.calls.count()).toBe(1, 'one call');
  });
});
