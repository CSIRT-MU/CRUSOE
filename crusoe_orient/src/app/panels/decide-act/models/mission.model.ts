export interface Configuration {
  configuration: {
    integrity: number;
    config_id: number;
    confidentiality: number;
    availability: number;
    time: string;
  };
  selected?: boolean;
}

export interface Mission {
  name: string;
  criticality: number;
  description: string;
  structure: string;
  configurations?: Configuration[];
  selectedConfig?: Configuration;
}

export interface Structure {
  relationships: {
    two_way: { from: number; to: number }[];
    one_way: { from: number; to: number }[];
  };
  support: { from: string; to: string }[];
  has_identity: { from: string; to: string }[];
  nodes: {
    missions: { name: string; criticality: number; description: string; id: number }[];
    hosts: { hostname: string; ip: string; id: number }[];
    services: { name: string; id: number }[];
    aggregations: { or: number[]; and: number[] };
  };
}
