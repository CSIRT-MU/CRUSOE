import { GeneralTask } from './general-task.model';
import { ActiveTask } from './active-task.model';
// Data returned by https://crusoe.csirt.muni.cz/flower/api/workers endpoint
// There is no endpoint, which would allow to get worker info by it's name

export interface Broker {
  hostname: string;
  userid?: any;
  virtual_host: string;
  port: number;
  insist: boolean;
  ssl: boolean;
  transport: string;
  connect_timeout: number;
  transport_options: any;
  login_method?: any;
  uri_prefix?: any;
  heartbeat: number;
  failover_strategy: string;
  alternates: any[];
}

export interface Inqueues {
  total: number;
  active: number;
}

export interface Writes {
  total: number;
  avg: string;
  all: string;
  raw: string;
  strategy: string;
  inqueues: Inqueues;
}

export interface Pool {
  'max-concurrency': number;
  processes: number[];
  'max-tasks-per-child': number;
  'put-guarded-by-semaphore': boolean;
  timeouts: number[];
  writes: Writes;
}

export interface Exchange {
  name: string;
  type: string;
  arguments?: any;
  durable: boolean;
  passive: boolean;
  auto_delete: boolean;
  delivery_mode?: any;
  no_declare: boolean;
}

export interface Queue {
  name: string;
  exchange: Exchange;
  routing_key: string;
  queue_arguments?: any;
  binding_arguments?: any;
  consumer_arguments?: any;
  durable: boolean;
  exclusive: boolean;
  auto_delete: boolean;
  no_ack: boolean;
  alias?: any;
  bindings: any[];
  no_declare?: any;
  expires?: any;
  message_ttl?: any;
  max_length?: any;
  max_length_bytes?: any;
  max_priority?: any;
}

export interface WorkerConf {
  accept_content: string[];
  beat_schedule: any;
  broker_url: string;
  crontab: string;
  enable_utc: boolean;
  result_backend: string;
  result_backend_transport_options: any;
  result_serializer: string;
  task_ignore_result: boolean;
  task_routes: any;
  task_serializer: string;
  worker_hijack_root_logger: boolean;
  worker_max_tasks_per_child: number;
  worker_redirect_stdouts: boolean;
  include: string[];
}

export interface Worker {
  stats: { pid: number; prefetch_count: number; pool: Pool; broker: Broker; total: any; rusage: any };
  active_queues: Queue[];
  total: any;
  active: ActiveTask[];
  scheduled: GeneralTask[];
  reserved: GeneralTask[];
  revoked: GeneralTask[];
  registered: string[];
  conf: WorkerConf;
}
