import { MessagingService } from 'src/app/shared/services/messaging.service';
import { ActivatedRoute } from '@angular/router';
import { Task } from './../models/tasks-data.model';
import { Component, OnInit } from '@angular/core';
import { TaskManagerService } from '../task-manager.service';

@Component({
  selector: 'app-task',
  templateUrl: './task.component.html',
  styleUrls: ['./task.component.scss'],
})
export class TaskComponent implements OnInit {
  currentTask: Task;
  taskID: string;
  taskLoading = true;

  constructor(private route: ActivatedRoute, private message: MessagingService, private tskmngr: TaskManagerService) {}

  ngOnInit(): void {
    this.taskID = this.route.snapshot.paramMap.get('id');
    this.fetchData();
  }

  public fetchData() {
    this.tskmngr.getTask(this.taskID).subscribe(
      (task: Task) => {
        this.currentTask = task;
        this.taskLoading = false;
      },
      (error: Error) => {
        this.message.showError('Unable to load task data.');
        this.taskLoading = false;
        console.error(error.message);
      }
    );
  }

  public showTaskState(state: string) {
    // const statusText = status ? 'Online' : 'Offline';
    return `<span class="state-label state-${state.toLowerCase()}">${state}</span>`;
  }
}
