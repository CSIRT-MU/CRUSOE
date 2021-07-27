// Data returned by https://crusoe.csirt.muni.cz/flower/tasks/datatable?...
// This is not API endpoint, I am using it because API endpoint does not support pagination and doesn't contain worker column
// I've opened issue and asked for pagination support https://github.com/mher/flower/issues/989
export interface Task {
  uuid: string;
  name: string;
  state: string;
  received: number;
  sent?: any;
  started: number;
  rejected?: any;
  succeeded: number;
  failed?: any;
  retried?: any;
  revoked?: any;
  args: string;
  kwargs: string;
  eta?: any;
  expires?: any;
  retries: number;
  worker: string;
  result: string;
  exception?: any;
  timestamp: number;
  runtime: number;
  traceback?: any;
  exchange?: any;
  routing_key?: any;
  clock: number;
  client?: any;
  root: string;
  root_id: string;
  parent: string;
  parent_id: string;
  children: any[];
}

export interface TasksData {
  draw: number;
  data: Task[];
  recordsFiltered: number;
  recordsTotal: number;
}
