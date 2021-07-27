/**
 * In GraphQL there is no such thing as "get all neighbours" using special character e.g. *.
 * Therefore, we have to manually define all attributes we want to fetch, in case we need to fetch "all neighbours".
 */
export const Attributes = {
  IP: `
  _id      
  address   
  resolves_to {
    _id
    domain_name
  } 
  source_of  {
    _id
    description
  }
  nodes   {
    _id
    topology_betweenness
    dependency_degree
    topology_degree
    is_a {
        _id
        softwareversions(first: 5) {
        _id
        version
        vulnerabilitys(first: 5) {
            _id
            description
            refers_to {
            _id
            CVE_id
            description
            }
        }
    }
  }
}
  part_of  {
    _id
    range
    note
  }`,
  DomainName: `
      _id
      domain_name
      tag
  `,
};
