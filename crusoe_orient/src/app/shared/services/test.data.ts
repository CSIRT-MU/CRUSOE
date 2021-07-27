export const TEST_IP_DATA = {
  data: {
    IP: [
      {
        __typename: 'IP',
        _id: '13416',
        address: '127.0.0.1',
        resolves_to: [{ __typename: 'DomainName', _id: '38955', domain_name: ['test.vpn.muni.cz.'] }],
        source_of: [],
        nodes: [
          {
            __typename: 'Node',
            _id: '13417',
            topology_betweenness: 0,
            dependency_degree: 0,
            topology_degree: 0,
            is_a: [
              {
                __typename: 'Host',
                _id: '725646',
                softwareversions: [
                  { __typename: 'SoftwareVersion', _id: '1099', version: '*:*:*', vulnerabilitys: [] },
                ],
              },
            ],
          },
        ],
        part_of: [{ __typename: 'Subnet', _id: '433104', range: '127.0.0.1/24', note: '' }],
      },
    ],
  },
};

export const TEST_NEIGHBOUR_NODE = {
  id: '12345',
  label: '8.8.8.8',
  data: {
    customColor: '#FF9800',
    type: 'IP',
    labelName: 'address',
    address: '8.8.8.8',
    color: '#aae3f5',
  },
  meta: { forceDimensions: false },
  dimension: { width: 113.5, height: 30 },
  position: { x: 76.75, y: 136 },
  transform: 'translate(20, 121)',
};

export const TEST_NEIGHBOUR_DATA = {
  data: {
    IP: [
      {
        __typename: 'IP',
        _id: '12345',
        address: '8.8.8.8',
        resolves_to: [{ __typename: 'DomainName', _id: '38955', domain_name: ['dns.muni.cz.'] }],
        source_of: [],
        nodes: [
          {
            __typename: 'Node',
            _id: '13417',
            topology_betweenness: 0,
            dependency_degree: 0,
            topology_degree: 0,
            is_a: [
              {
                __typename: 'Host',
                _id: '725646',
                softwareversions: [
                  { __typename: 'SoftwareVersion', _id: '1099', version: '*:*:*', vulnerabilitys: [] },
                ],
              },
            ],
          },
        ],
        part_of: [{ __typename: 'Subnet', _id: '433104', range: '8.8.8.8/24', note: '' }],
      },
    ],
  },
};
