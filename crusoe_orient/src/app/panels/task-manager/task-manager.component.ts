import { environment } from 'src/environments/environment.prod';
import { MessagingService } from 'src/app/shared/services/messaging.service';
import { Component, OnInit, ViewChild, OnDestroy } from '@angular/core';
import { TaskManagerService } from './task-manager.service';
import { DashboardData, DashboardDataItem } from './models/dashboard-data.model';
import { Subscription, timer } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { MatTable } from '@angular/material/table';
import { Task, TasksData } from './models/tasks-data.model';
import { PageEvent } from '@angular/material/paginator';
import { Title } from '@angular/platform-browser';
import { Sort } from '@angular/material/sort';

@Component({
  selector: 'app-task-manager',
  templateUrl: './task-manager.component.html',
  styleUrls: ['./task-manager.component.scss'],
})
export class TaskManagerComponent implements OnInit, OnDestroy {
  title = 'Task Manager';
  dashboardData: DashboardDataItem[] = [];
  workersColumns = ['hostname', 'status', 'active', 'processed', 'failed', 'succeeded', 'retried', 'loadavg'];
  subscription: Subscription;
  activeTasks: number;
  failedTasks: number;
  succeededTasks: number;
  retriedTasks: number;
  tasks: Task[];
  tasksColumns = ['name', 'uuid', 'state', 'args', 'kwargs', 'result', 'received', 'started', 'runtime', 'worker'];
  tasksTotal: number;
  tasksPageSize = 10;
  tasksCurrentPage = 0;
  dashboardLoading = true;
  initialTasksLoading = true;
  searchString = '';
  order = 'desc';

  // Pie chart options
  gradient = true;
  showLegend = true;
  showLabels = true;
  isDoughnut = false;

  colorScheme = {
    domain: ['#005bea', '#029666', '#f93a5a', '#f76a2d'],
  };

  piechartData: any[];

  @ViewChild(MatTable) table: MatTable<any>;

  constructor(private tskmngr: TaskManagerService, private message: MessagingService, private titleService: Title) {
    this.titleService.setTitle(this.title + ' - ' + environment.applicationName);
  }

  onSelect(data): void {
    // console.log('Item clicked', data);
  }

  ngOnInit(): void {
    this.subscription = timer(0, 1500)
      .pipe(switchMap(() => this.tskmngr.getDashboard()))
      .subscribe(
        (data: DashboardData) => {
          this.dashboardData = data.data;
          // When there will be more workers, this needs to be replaced by iteration over data
          this.activeTasks = isNaN(data.data[0].active) ? 0 : data.data[0].active;
          this.failedTasks = isNaN(data.data[0]['task-failed']) ? 0 : data.data[0]['task-failed'];
          this.succeededTasks = isNaN(data.data[0]['task-succeeded']) ? 0 : data.data[0]['task-succeeded'];
          this.retriedTasks = isNaN(data.data[0]['task-retried']) ? 0 : data.data[0]['task-retried'];
          this.dashboardLoading = false;
          if (this.table) {
            this.table.renderRows();
          }
          this.piechartData = [
            { name: 'Active tasks', value: this.activeTasks },
            { name: 'Succeeded tasks', value: this.succeededTasks },
            { name: 'Failed tasks', value: this.failedTasks },
            { name: 'Retried tasks', value: this.retriedTasks },
          ];
        },
        (_) => {
          this.dashboardLoading = false;
          this.message.showError('Error loading data.');
        }
      );
    this.fetchTasks(this.tasksCurrentPage, this.tasksPageSize, null);
  }

  ngOnDestroy(): void {
    this.subscription.unsubscribe();
  }

  public showWorkerStatus(status: Boolean) {
    const statusText = status ? 'Online' : 'Offline';
    return `<span class="status-label ${statusText.toLowerCase()}">${statusText}</span>`;
  }

  public showTaskState(state: string) {
    // const statusText = status ? 'Online' : 'Offline';
    return `<span class="state-label state-${state.toLowerCase()}">${state}</span>`;
  }

  private fetchTasks(start: number, total: number, order: string, searchValue?: string, state?: string) {
    if (!order) {
      order = this.order;
    }

    this.initialTasksLoading = true;
    this.tskmngr.getTasks(start, total, order, searchValue || '').subscribe(
      (taskData: TasksData) => {
        this.tasks = Array.from(taskData.data);
        // .sort((a: Task, b: Task) => {
        //   if (a.started < b.started) {
        //     return 1;
        //   } else if (a.started > b.started) {
        //     return -1;
        //   }
        //   return 0;
        // });

        this.tasksTotal = taskData.recordsFiltered;
        this.initialTasksLoading = false;
      },
      (_) => {
        this.initialTasksLoading = false;
        this.message.showError('Error loading tasks. Please try again later.');
      }
    );
  }

  public tasksPaginatorChange(event: PageEvent) {
    this.tasksPageSize = event.pageSize;
    this.tasksCurrentPage = event.pageIndex;
    this.fetchTasks(event.pageIndex * this.tasksPageSize, this.tasksPageSize, null);
  }

  applyFilter(searchString: string) {
    this.searchString = searchString;
    this.fetchTasks(this.tasksCurrentPage, this.tasksPageSize, null, searchString);
  }

  roundTime(time: number) {
    return Math.round(time * 100) / 100;
  }

  epochToDatetime(epoch: number) {
    if (!epoch) {
      return '-';
    }

    const d = new Date(epoch * 1000);
    const dateString =
      d.getDate() +
      '. ' +
      (d.getMonth() + 1) +
      '. ' +
      d.getFullYear() +
      ' ' +
      this.paddNumber(d.getHours()) +
      ':' +
      this.paddNumber(d.getMinutes()) +
      ':' +
      this.paddNumber(d.getSeconds());
    return dateString;
  }

  paddNumber(d: number) {
    return String('0' + d).slice(-2);
  }

  sortData(sort: Sort) {
    this.order = sort.direction;
    this.fetchTasks(this.tasksCurrentPage, this.tasksPageSize, this.order, this.searchString);
  }
}
