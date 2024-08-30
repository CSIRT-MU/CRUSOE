import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
import { Observable } from 'rxjs';
import { DashboardData } from './models/dashboard-data.model';
import { TasksData, Task } from './models/tasks-data.model';
import { map } from 'rxjs/operators';
import { Worker } from './models/workers-data.model';

@Injectable({
  providedIn: 'root',
})
export class TaskManagerService {
  constructor(private http: HttpClient) {}

  /**
   * Return overview data from Flower API
   */
  getDashboard(): Observable<DashboardData> {
    return this.http.get<DashboardData>(environment.flowerUrl + 'dashboard?json=1');
  }

  /**
   * Return tasks
   * @param start
   * @param limit
   * @param searchValue
   * @param order - asc/desc
   */
  getTasks(start: number, limit: number, order?: string, searchValue?: string): Observable<TasksData> {
    if (!searchValue) {
      searchValue = '';
    }

    if (!order) {
      order = 'desc';
    }

    // This URL is ugly, because Flower API is ugly
    const tasksUglyUrl = encodeURI(
      `tasks/datatable?draw=1&columns[0][data]=name&columns[0][name]=&columns[0][searchable]=true&columns[0][orderable]=true&columns[0][search][value]=&columns[0][search][regex]=false&columns[1][data]=uuid&columns[1][name]=&columns[1][searchable]=true&columns[1][orderable]=false&columns[1][search][value]=&columns[1][search][regex]=false&columns[2][data]=state&columns[2][name]=&columns[2][searchable]=true&columns[2][orderable]=true&columns[2][search][value]=&columns[2][search][regex]=false&columns[3][data]=args&columns[3][name]=&columns[3][searchable]=true&columns[3][orderable]=true&columns[3][search][value]=&columns[3][search][regex]=false&columns[4][data]=kwargs&columns[4][name]=&columns[4][searchable]=true&columns[4][orderable]=true&columns[4][search][value]=&columns[4][search][regex]=false&columns[5][data]=result&columns[5][name]=&columns[5][searchable]=true&columns[5][orderable]=true&columns[5][search][value]=&columns[5][search][regex]=false&columns[6][data]=received&columns[6][name]=&columns[6][searchable]=true&columns[6][orderable]=true&columns[6][search][value]=&columns[6][search][regex]=false&columns[7][data]=started&columns[7][name]=&columns[7][searchable]=true&columns[7][orderable]=true&columns[7][search][value]=&columns[7][search][regex]=false&columns[8][data]=runtime&columns[8][name]=&columns[8][searchable]=true&columns[8][orderable]=true&columns[8][search][value]=&columns[8][search][regex]=false&columns[9][data]=worker&columns[9][name]=&columns[9][searchable]=true&columns[9][orderable]=true&columns[9][search][value]=&columns[9][search][regex]=false&columns[10][data]=exchange&columns[10][name]=&columns[10][searchable]=true&columns[10][orderable]=true&columns[10][search][value]=&columns[10][search][regex]=false&columns[11][data]=routing_key&columns[11][name]=&columns[11][searchable]=true&columns[11][orderable]=true&columns[11][search][value]=&columns[11][search][regex]=false&columns[12][data]=retries&columns[12][name]=&columns[12][searchable]=true&columns[12][orderable]=true&columns[12][search][value]=&columns[12][search][regex]=false&columns[13][data]=revoked&columns[13][name]=&columns[13][searchable]=true&columns[13][orderable]=true&columns[13][search][value]=&columns[13][search][regex]=false&columns[14][data]=exception&columns[14][name]=&columns[14][searchable]=true&columns[14][orderable]=true&columns[14][search][value]=&columns[14][search][regex]=false&columns[15][data]=expires&columns[15][name]=&columns[15][searchable]=true&columns[15][orderable]=true&columns[15][search][value]=&columns[15][search][regex]=false&columns[16][data]=eta&columns[16][name]=&columns[16][searchable]=true&columns[16][orderable]=true&columns[16][search][value]=&columns[16][search][regex]=false&order[0][column]=7&order[0][dir]=${order}&start=${start}&length=${limit}&search[value]=${searchValue}&search[regex]=false`
    );
    return this.http.get<TasksData>(environment.flowerUrl + tasksUglyUrl);
  }

  /**
   * Returns detail about given task
   * @param uuid
   */
  getTask(uuid: string): Observable<Task> {
    return this.http.get<Task>(environment.flowerUrl + 'api/task/info/' + uuid);
  }

  /**
   * Return workers
   */
  getWorkers(): Observable<any> {
    return this.http.get<any>(environment.flowerUrl + 'api/workers?refresh=1');
  }

  /**
   * Returns info about the worker
   * @param workerName
   */
  getWorker(workerName: string): Observable<Worker> {
    return this.http.get<any>(environment.flowerUrl + 'api/workers?refresh=1').pipe(
      map(function (data: any): Worker {
        if (!data[workerName]) {
          throw new Error('Worker data not found');
        }
        return data[workerName];
      })
    );
  }

  /**
   * Grows pool by given value
   * @param workerName
   * @param shrinkSize
   */
  poolSizeGrow(workerName: string, shrinkSize: number) {
    const data = {
      workername: workerName,
      n: shrinkSize,
    };

    const httpOptions = {
      headers: new HttpHeaders({
        'Content-type': 'application/json',
      }),
    };

    return this.http.post(environment.flowerUrl + 'api/worker/pool/grow/' + workerName, data, httpOptions);
  }

  /**
   * Shrinks pool by given value
   * @param workerName
   * @param shrinkSize
   */
  poolSizeShrink(workerName: string, shrinkSize: number) {
    const data = {
      workername: workerName,
      n: shrinkSize,
    };

    const httpOptions = {
      headers: new HttpHeaders({
        'Content-type': 'application/json',
      }),
    };

    return this.http.post(environment.flowerUrl + 'api/worker/pool/shrink/' + workerName, data, httpOptions);
  }

  /**
   * Changes autoscale values for pool
   * @param workerName
   * @param min
   * @param max
   */
  poolAutoscale(workerName: string, min: number, max: number) {
    const data = {
      workername: workerName,
      min: min,
      max: max,
    };

    const httpOptions = {
      headers: new HttpHeaders({
        'Content-type': 'application/json',
      }),
    };

    return this.http.post(environment.flowerUrl + 'api/worker/pool/autoscale/' + workerName, data, httpOptions);
  }

  /**
   * Cancels consumer
   * @param workerName
   * @param queue
   */
  cancelConsumer(workerName: string, queue: string) {
    const data = {
      workername: workerName,
      queue: queue,
    };

    const httpOptions = {
      headers: new HttpHeaders({
        'Content-type': 'application/json',
      }),
    };

    return this.http.post(
      environment.flowerUrl + 'api/worker/queue/cancel-consumer/' + workerName,
      data,
      httpOptions
    );
  }

  /**
   * Edits task timeout
   * @param workerName
   * @param taskName
   * @param timeout
   */
  editTaskTimeout(workerName: string, taskName: string, timeout: number) {
    const data = {
      workername: workerName,
      type: String(timeout),
    };

    const httpOptions = {
      headers: new HttpHeaders({
        'Content-type': 'application/json',
      }),
    };

    return this.http.post(environment.flowerUrl + 'api/task/timeout/' + taskName, data, httpOptions);
  }

  /**
   * Edits task ratelimit
   * @param workerName
   * @param taskName
   * @param ratelimit
   */
  editTaskRateLimit(workerName: string, taskName: string, ratelimit: number) {
    const data = {
      workername: workerName,
      ratelimit: String(ratelimit),
    };

    const httpOptions = {
      headers: new HttpHeaders({
        'Content-type': 'application/json',
      }),
    };

    return this.http.post(environment.flowerUrl + 'api/task/rate-limit/' + taskName, data, httpOptions);
  }
}
