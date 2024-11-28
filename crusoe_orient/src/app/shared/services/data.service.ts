import { Injectable } from '@angular/core';
import { Apollo } from 'apollo-angular';
import { Observable, throwError } from 'rxjs';
import gql from 'graphql-tag';
import { GraphInput } from 'src/app/shared/models/graph.model';
import { Node, Edge } from '@swimlane/ngx-graph';
import { entities } from 'src/app/shared/config/network-visualization.config';
import _ from 'lodash';
import { tap, map } from 'rxjs/operators';
import { Attributes } from 'src/app/shared/config/attributes';
import { CVEResponse, CVE } from 'src/app/shared/models/vulnerability.model';
import { VulnerabilityData } from '../../panels/vulnerability/vulnerability.component';
import { Subnet } from 'src/app/shared/models/subnet.model';
import { DocumentNode } from 'graphql';
import { ComparatorService } from './comparator.service';
import { Mission } from 'src/app/panels/decide-act/models/mission.model';
import { MissionStructure } from 'src/app/panels/decide-act/models/mission-structure.model';

@Injectable({
  providedIn: 'root',
})
export class DataService {
  constructor(private apollo: Apollo) {}

  /**
   * Get IP node from database based on IP address
   * @param ip
   */
  public getIPNode(ip: string): Observable<GraphInput> {
    return this.apollo
      .query<any>({
        query: gql`
        {
          IP(address: "${ip}") {
            ${this.getAttributesOfType('IP')}
          }
        }
      `,
      })
      .pipe(
        map((data) => {
          const { nodes, edges } = this.converToGraph(data.data.IP);
          return { nodes, edges };
        })
      );
  }

  public getTraversalParameters(): Observable<{ subnets: Subnet[]; missions: string[] }> {
    return this.apollo // Assuming 'this' has an Apollo instance
      .query<any>({
        query: gql`
          {
            Subnet {
              note
              range
            }
            Mission {
              name
            }
          }
        `,
      })
      .pipe(
        map((data) => {
          // Assuming the response structure has a 'Subnet' property
          const subnetsData = data.data.Subnet;
          const missions = data.data.Mission.map((mission: any) => mission.name);
          if (!subnetsData) {
            return { subnets: [], missions: [] }; // Return an empty array if no subnets found
          }
          let subnets: Subnet[] = [];
          subnetsData.forEach((item) => {
            subnets.push({
              note: item.note,
              range: item.range,
            });
          });
          return { subnets, missions };
        })
      );
  }

  public getIPSubnet(ip: string): Observable<string> {
    return this.apollo // Assuming 'this' has an Apollo instance
      .query<any>({
        query: gql`
        {
          IP(address: "${ip}"){
            part_of {
              range
            }
          }
        }
        `,
      })
      .pipe(
        map((data) => {
          return data.data.IP[0].part_of[0].range;
        })
      );
  }

  /**
   * Gets neighbours of given node
   * @param node
   */
  public getNodeNeighbours(node: Node): Observable<GraphInput> {
    console.log(node, JSON.stringify(node));
    return this.apollo
      .query<any>({
        query: gql`
        {
          ${node.data.type}(_id: "${node.id}") {
            ${this.getAttributesOfType(node.data.type)}
          }
        }
      `,
      })
      .pipe(
        map((data) => {
          const { nodes, edges } = this.converToGraph(data.data[node.data.type]);
          return { nodes, edges };
        })
      );
  }

  /**
   * Get IP node from database based on IP address
   * @param ip
   */
  public getTraversalBase(ip: string, subnet: string, mission: string): Observable<GraphInput> {
    const query = this.buildIpQuery(ip, subnet, mission);
    return this.apollo
      .query<any>({ query: query })
      .pipe(
        map((data) => {
          // Find the IP with matching address
          const matchingIp = data.data.IP.find((ipData) => ipData.address === ip);

          // Check if matching IP is found
          if (!matchingIp) throw new Error(`No IP found with address: ${ip}`);

          const { nodes, edges } = this.constructBN(
            matchingIp,
            data.data.IP,
            data.data.total_cve_count,
            data.data.total_event_count
          );
          return { nodes, edges };
        })
      );
  }

  private buildIpQuery(ip: string, subnet: string, mission: string): DocumentNode {
    if (mission) {
      return gql`
      {
        IP(filter: {
          OR: [
            {
              nodes_in: {
                is_a_in: {
                  components_in: {
                    supports_some: {
                      name: "${mission}"
                    }
                  }
                }
              }
            },
            {
              address: "${ip}"
            }
          ]
        }) {
          ${this.getAttributesOfType('expanded_IP')}
        }
        total_event_count,
        total_cve_count
      }
      `;
    }
    return gql`
    {
      IP(filter: {
        OR: [
          {
            part_of: {
              range: "${subnet}"
            }
          },
          {
            address: "${ip}"
          }
        ]
      }) {
        ${this.getAttributesOfType('expanded_IP')}
      }
      total_event_count,
      total_cve_count
    }
    `;
  }
  getAttributesOfType(type: any): string {
    return Attributes[type].toString();
  }

  /**
   * Converts graph data to ngx-graph compliant format
   * @param data
   * @param parent
   * @param edgeName
   */
  public converToGraph(data: any[], parent?: string, edgeName?: string): GraphInput {
    let nodes: Node[] = [];
    let edges: Edge[] = [];

    data.forEach((item) => {
      if (nodes.findIndex((n) => n.id === item._id) === -1) {
        nodes.push({
          id: item._id,
          label: this.getLabel(item),
          data: {
            customColor: this.getColor(item),
            type: item.__typename,
            labelName: this.getLabelName(item),
            ...this.clearAttributes(item),
          },
        });
      }

      if (parent) {
        edges.push({ source: parent, target: item._id, label: edgeName });
      }

      Object.keys(item).forEach((key) => {
        if (Array.isArray(item[key]) && item[key].length > 0 && item[key][0].__typename) {
          const { nodes: newNodes, edges: newEdges } = this.converToGraph(item[key], item._id, key);
          nodes = _.unionBy(nodes, newNodes, (n) => n.id);
          edges = _.unionBy(edges, newEdges, (e) => [e.source, e.target, e.label]);
        }
      });
    });

    return { nodes, edges };
  }

  /**
   * Converts graph data to ngx-graph compliant format
   * @param root_ip
   * @param data
   * @param cve_count
   * @param event_count
   */
  public constructBN(root_ip: any, data: any[], cve_count: number, event_count: number): GraphInput {
    let nodes: Node[] = [];
    let edges: Edge[] = [];

    console.log(data);

    data.forEach((item) => {
      if (nodes.findIndex((n) => n.id === item._id) === -1) {
        nodes.push({
          id: item._id,
          label: this.getLabel(item),
          data: {
            similarity: {},
            customColor: this.getColor(item),
          },
        });
      }
    });

    const root_index = nodes.findIndex((node) => node.label === root_ip.address);
    nodes[root_index].data.customColor = 'red';
    let previous_iter: Node[] = [nodes[root_index]];
    const comparator = new ComparatorService(cve_count, event_count);

    let addedNewEdge = true;
    while (addedNewEdge) {
      addedNewEdge = false;
      let current_processed: Node[] = [];

      for (const source of previous_iter) {
        for (const target of nodes) {
          if (this.canAddEdge(source, target, edges)) {
            const sourceData = data.find((item) => item._id === source.id);
            const targetData = data.find((item) => item._id === target.id);
            const riskScore = comparator.calculateRiskScore(sourceData, targetData);
            if (riskScore > comparator.threshold) {
              if (!current_processed.find((node) => node.id === target.id)) {
                current_processed.push(target);
              }
              edges.push({ source: source.id, target: target.id });
              target.data.similarity[source.label] = riskScore;
              addedNewEdge = true;
            }
          }
        }
      }
      previous_iter = [...current_processed];
    }
    // Change the ID of the root node to 0 so it's on top in the graph
    // Only if there isn't 0 already present
    if (!nodes.some((node) => node.id === '0')) {
      const root_id = nodes[root_index].id;
      nodes[root_index].id = '0';
      edges.forEach((edge) => (edge.source === root_id ? (edge.source = '0') : null));
    }
    return { nodes, edges };
  }

  private canAddEdge(from: Node, to: Node, edges: Edge[]): boolean {
    if (from.id === to.id) return false;
    if (edges.some((edge) => edge.source === from.id && edge.target === to.id)) {
      return false;
    }

    const stack: string[] = [to.id];
    const visited: Set<string> = new Set();

    while (stack.length) {
      const node = stack.pop()!; // Guaranteed to have a value due to initial push

      if (visited.has(node)) {
        continue; // Skip already visited nodes
      }

      if (node === from.id) {
        return false; // Found the target node
      }

      visited.add(node);

      const outgoingEdges = edges.filter((edge) => edge.source === node);
      for (const edge of outgoingEdges) {
        stack.push(edge.target); // Push neighbors onto the stack
      }
    }

    return true; // Not reachable after all neighbors are explored
  }

  /**
   * Gets label of given node based on static config
   * @param node
   */
  public getLabel(node: any): string {
    const initialLabel = node.__typename;
    if (typeof entities[initialLabel] === 'undefined') {
      return initialLabel;
    }
    if (entities[initialLabel].showProperty.length === 0) {
      return initialLabel;
    }
    const propKey = entities[initialLabel].showProperty.find(
      (pk) => typeof node[pk] !== 'undefined' && node[pk] !== null
    );
    if (typeof node[propKey] === 'undefined') {
      return initialLabel;
    }
    return node[propKey].toString();
  }

  /**
   * Gets label name of given node (eg. DomainName, IP)
   * @param node
   */
  public getLabelName(node: any): string {
    const initialLabel = node.__typename;
    if (typeof entities[initialLabel] === 'undefined') {
      return initialLabel;
    }
    if (entities[initialLabel].showProperty.length === 0) {
      return initialLabel;
    }
    const propKey = entities[initialLabel].showProperty.find(
      (pk) => typeof node[pk] !== 'undefined' && node[pk] !== null
    );
    if (typeof node[propKey] === 'undefined') {
      return initialLabel;
    }
    return propKey;
  }

  /**
   * Return color that should be assigned to given node
   * @param node
   */
  private getColor(node: any): string {
    const initialLabel = node.__typename;
    return entities[initialLabel]?.bgColor || 'red';
  }

  /**
   * Clears unneccessery attributes of item
   * @param item
   */
  private clearAttributes(item: any) {
    const clonedItem = { ...item };
    delete clonedItem._id;
    delete clonedItem.__typename;
    return clonedItem;
  }

  /**
   * Returns label of ngx-graph node based on static config
   * @param node
   */
  public getLabelOfGraphNode(node: Node) {
    const initialLabel = node.data.type;
    if (typeof entities[initialLabel] === 'undefined') {
      return initialLabel;
    }
    if (entities[initialLabel].showProperty.length === 0) {
      return initialLabel;
    }
    const propKey = entities[initialLabel].showProperty.find(
      (pk) => typeof node.data[pk] !== 'undefined' && node.data[pk] !== null
    );
    if (typeof node.data[propKey] === 'undefined') {
      return initialLabel;
    }
    return node.data[propKey].toString();
  }

  /**
   * Returns vulnerable machines (software version, ip address, domain, subnet)
   * @param cveCode CVE code of vulnerability
   */
  public getVulnerableMachines(cveCode: string): Observable<VulnerabilityData[]> {
    return this.apollo
      .query<CVEResponse>({
        query: gql`
      {
        CVE(filter: {CVE_id_contains: "${cveCode}"}) {
          vulnerabilitys {
            in {
              version
              on {
                _id
                nodes(first: 500) {
                  _id
                  has_assigned {
                    _id
                    address
                    resolves_to {
                      domain_name
                    }
                    part_of {
                      note
                      range
                    }
                  }
                }
              }
            }
          }
        }
      }
      `,
      })
      .pipe(
        map((response) => {
          const responseArray: VulnerabilityData[] = [];
          if (!response.data.CVE[0]) {
            return null;
          }
          response.data.CVE[0].vulnerabilitys.forEach((vuln) => {
            vuln.in.forEach((software) => {
              _.uniqBy(software.on, (n) => n._id).forEach((host) => {
                host.nodes.forEach((node) => {
                  node.has_assigned.forEach((ip) => {
                    let subnet = '';
                    let domain = '';
                    if (ip.part_of[0]) {
                      subnet = `${ip.part_of[0].range}`;
                      if (ip.part_of[0].note) {
                        subnet += ` (${ip.part_of[0].note})`;
                      }
                    }
                    if (ip.resolves_to[0]) {
                      domain = ip.resolves_to[0].domain_name.toString();
                    }
                    responseArray.push({
                      domainName: domain,
                      subnet: subnet,
                      ip: ip.address,
                      software: software.version,
                    });
                  });
                });
              });
            });
          });
          return responseArray;
        })
      );
  }

  /**
   * Returns the description of vulnerability
   */
  public getCVEDetails(cveCode: string): Observable<CVE> {
    return this.apollo
      .query<{ CVE: CVE[] }>({
        query: gql`
      {
        CVE(filter: {CVE_id_contains: "${cveCode}"}) {
          description
          access_complexity
          access_vector
          attack_complexity
          attack_vector
          authentication
          availability_impact_v2
          availability_impact_v3
          base_score_v2
          base_score_v3
          confidentiality_impact_v2
          confidentiality_impact_v3
          description
          integrity_impact_v2
          integrity_impact_v3
          obtain_all_privilege
          obtain_other_privilege
          obtain_user_privilege
          privileges_required
          published_date
          scope
          user_interaction
          impact
        }
      }
      `,
      })
      .pipe(
        map((response) => {
          return response.data.CVE[0];
        })
      );
  }

  /**
   * Gets names of all available missions
   */
  public getMissionNames(): Observable<string[]> {
    return this.apollo // Assuming 'this' has an Apollo instance
      .query<any>({
        query: gql`
          {
            Mission {
              name
            }
          }
        `,
      })
      .pipe(
        map((data) => {
          const missions = data.data.Mission.map((mission: any) => mission.name);
          return missions;
        })
      );
  }

  /**
   * Gets mission object by its name
   * @param name name of the mission
   */
  public getMission(name: String): Observable<Mission[]> {
    return this.apollo // Assuming 'this' has an Apollo instance
    .query<any>({
      query: gql`
        {
          Mission(name: "${name}") {
            name,
            criticality,
            description,
            structure,
          }
        }
      `,
    })
    .pipe(
      map((response) => {
        const missions: Mission[] = response.data.Mission
        return missions;
      })
    );
  }

  /**
   * Gets structure parameter from each mission and merges them into one structure
   * @param missions list of missions
   *
   */
  public makeMissionsStructure(missions: Mission[]): MissionStructure {
    let result: MissionStructure;
    let structure: MissionStructure;

    result = missions.reduce(
      (acc, mission) => {
        structure = JSON.parse(mission.structure);
        return {
          nodes: {
            missions: [...acc.nodes.missions, ...structure.nodes.missions],
            hosts: [...acc.nodes.hosts, ...structure.nodes.hosts],
            services: [...acc.nodes.services, ...structure.nodes.services],
            aggregations: {
              or: [...acc.nodes.aggregations.or, ...structure.nodes.aggregations.or],
              and: [...acc.nodes.aggregations.and, ...structure.nodes.aggregations.and],
            },
          },
          relationships: {
            two_way: [...acc.relationships.two_way, ...structure.relationships.two_way],
            one_way: [...acc.relationships.one_way, ...structure.relationships.one_way],
            supports: [...acc.relationships.supports, ...structure.relationships.supports],
            has_identity: [...acc.relationships.has_identity, ...structure.relationships.has_identity],
          },
        };
      },
      {
        nodes: { missions: [], hosts: [], aggregations: { and: [], or: [] }, services: [] },
        relationships: { two_way: [], one_way: [], supports: [], has_identity: [] },
      }
    );

    return result;
  }
}

