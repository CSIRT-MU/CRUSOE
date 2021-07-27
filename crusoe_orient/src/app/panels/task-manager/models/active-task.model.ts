export interface ActiveTask {
  id: string;
  name: string;
  args: string;
  kwargs: string;
  type: string;
  hostname: string;
  time_start: number;
  acknowledged: boolean;
  delivery_info: { exchange: string; routing_key: string; priority: number; redelivered: any };
  worker_pid: number;
}
