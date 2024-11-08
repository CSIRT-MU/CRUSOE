export const comparator_config = {
  max_distance: 2,
  path: {
    apply: true,
    subnet: 1,
    organization_unit: 1.25,
    contact: 1.15,
  },
  comparators: {
    os: {
      apply: true,
      critical_bound: 0.34927222,
      diff_value: 0.2,
      vendor: 0.9,
      product: 0.075,
      version: 0.025,
    },
    antivirus: {
      apply: true,
      critical_bound: 0.5,
      diff_value: 0.4,
      vendor: 0.6,
      product: 0.25,
      version: 0.15,
    },
    cms: {
      apply: true,
      require_open_ports: false,
      critical_bound: 0.44568431,
      diff_value: 0.4,
      vendor: 0.6,
      product: 0.25,
      version: 0.15,
    },
    net_service: {
      apply: true,
      critical_bound: 0.25,
      diff_value: 0.1,
    },
    cve_cumulative: {
      apply: true,
      critical_bound: 0.29492334,
    },
    event_cumulative: {
      apply: true,
      critical_bound: 0.00036752,
    },
  },
};
