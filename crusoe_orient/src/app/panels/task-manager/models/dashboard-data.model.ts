// Data returned by https://crusoe.csirt.muni.cz/flower/dashboard?json=1
export interface DashboardDataItem {
  'worker-heartbeat': number;
  'task-received': number;
  'task-started': number;
  'task-succeeded': number;
  'task-failed': number;
  'task-retried': number;
  hostname: string;
  pid: number;
  freq: number;
  heartbeats: number[];
  clock: number;
  active: number;
  processed: number;
  loadavg: number[];
  sw_ident: string;
  sw_ver: string;
  sw_sys: string;
  status: boolean;
}

export interface DashboardData {
  data: DashboardDataItem[];
}
