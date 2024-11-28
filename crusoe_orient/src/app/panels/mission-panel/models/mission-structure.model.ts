export interface OneWay {
  from: number;
  to: number;
}

export interface Support {
  from: string;
  to: string;
}

export interface HasIdentity {
  from: string;
  to: string;
}

export interface Relationships {
  two_way: any[];
  one_way: OneWay[];
  supports: Support[];
  has_identity: HasIdentity[];
}

export interface Mission {
  name: string;
  criticality: number;
  description: string;
  id: number;
}

export interface Host {
  hostname: string;
  ip: string;
  id: number;
}

export interface Service {
  name: string;
  id: number;
}

export interface Aggregations {
  or: number[];
  and: number[];
}

export interface Nodes {
  missions: Mission[];
  hosts: Host[];
  services: Service[];
  aggregations: Aggregations;
}

export interface MissionStructure {
  relationships: Relationships;
  nodes: Nodes;
}
