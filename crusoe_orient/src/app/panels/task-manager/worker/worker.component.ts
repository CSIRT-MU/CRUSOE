import { MessagingService } from 'src/app/shared/services/messaging.service';
import { GeneralTask } from './../models/general-task.model';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { TaskManagerService } from '../task-manager.service';
import { Worker, Queue } from '../models/workers-data.model';
import { ActiveTask } from '../models/active-task.model';

@Component({
  selector: 'app-worker',
  templateUrl: './worker.component.html',
  styleUrls: ['./worker.component.scss'],
})
export class WorkerComponent implements OnInit {
  queuesColumns: string[] = [
    'name',
    'exclusive',
    'durable',
    'routing_key',
    'no_ack',
    'alias',
    'queue_arguments',
    'binding_arguments',
    'auto_delete',
    'cancel_queue',
  ];
  activeQueues: Queue[];
  workerName: string;
  workerData: Worker;
  JSON: any;
  processedTasks: { name: string; value: number }[] = [];
  activeTasks: ActiveTask[];
  scheduledTasks: GeneralTask[];
  reservedTasks: GeneralTask[];
  revokedTasks: GeneralTask[];
  registeredTasks: string[];
  workerConfTable: { name: string; value: any }[] = [];
  usageStatistics: { name: string; value: any }[] = [];

  constructor(private route: ActivatedRoute, private tskmngr: TaskManagerService, private message: MessagingService) {
    this.JSON = JSON;
  }

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    this.workerName = id;
    this.fetchData();
  }

  public fetchData() {
    this.tskmngr.getWorker(this.workerName).subscribe(
      (worker: Worker) => {
        this.workerData = worker;
        this.activeQueues = this.workerData.active_queues;

        for (const [key, value] of Object.entries(this.workerData.stats.total)) {
          this.processedTasks.push({ name: key, value: Number(value) });
        }

        this.activeTasks = this.workerData.active;
        this.scheduledTasks = this.workerData.scheduled;
        this.revokedTasks = this.workerData.revoked;
        this.registeredTasks = this.workerData.registered;

        for (const [key, value] of Object.entries(this.workerData.stats.rusage)) {
          this.usageStatistics.push({ name: key, value: value });
        }

        for (const [key, value] of Object.entries(this.workerData.conf)) {
          this.workerConfTable.push({ name: key, value: value });
        }
      },
      (error: Error) => {
        this.message.showError('Unable to load worker data.');
        console.error(error.message);
      }
    );
  }

  public growPool(size: number) {
    this.tskmngr.poolSizeGrow(this.workerName, size).subscribe(
      (_) => {
        this.message.showSuccess('Pool size updated.');
      },
      (_) => {
        this.message.showError('Error while updating pool size. Check developer console for more info.');
      }
    );
  }

  public shrinkPool(size: number) {
    this.tskmngr.poolSizeShrink(this.workerName, size).subscribe(
      (data) => {
        this.message.showSuccess(data['message']);
      },
      (data) => {
        this.message.showError(data['responseText']);
      }
    );
  }

  public cancelConsumer(name: string) {
    this.tskmngr.cancelConsumer(this.workerName, name).subscribe(
      (data) => {
        this.message.showSuccess(data['message']);
      },
      (error) => {
        this.message.showError(error['responseText']);
      }
    );
  }

  public editTaskTimeout(taskName: string, timeout: number) {
    this.tskmngr.editTaskTimeout(this.workerName, taskName, timeout).subscribe(
      (data) => {
        this.message.showSuccess(data['message']);
      },
      (error) => {
        this.message.showError(error['responseText']);
      }
    );
  }

  public editRatelimit(taskName: string, ratelimit: number) {
    this.tskmngr.editTaskRateLimit(this.workerName, taskName, ratelimit).subscribe(
      (data) => {
        this.message.showSuccess(data['message']);
      },
      (error) => {
        this.message.showError(error['responseText']);
      }
    );
  }
}
