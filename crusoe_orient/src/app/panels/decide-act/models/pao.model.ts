import { PaoStatus } from './pao-status.model';
export interface Pao {
  port: number;
  ip: string;
  pao: string;
  status: PaoStatus;
  maxCapacity?: number;
  usedCapacity?: number;
}

export interface PaoResponse {
  paos: Pao[];
}
