import { Component, OnInit, Input } from '@angular/core';
import { Node, Edge, Layout } from '@swimlane/ngx-graph';
import { Structure } from '../models/mission.model';
import { CustomLayout } from '../missions-graph/custom-layout';
import { Subject } from 'rxjs';
import { Router } from '@angular/router';
import { MissionStructure } from '../models/mission-structure.model';

@Component({
  selector: 'app-missions-graph',
  templateUrl: './missions-graph.component.html',
  styleUrls: ['./missions-graph.component.scss'],
})
export class MissionsGraphComponent implements OnInit {
  edges: Edge[];
  nodes: Node[];
  title: string;
  description: string;
  loading = true;
  error = false;
  customLayout: Layout = new CustomLayout();
  center$ = new Subject<any>();
  @Input() structure: MissionStructure;
  @Input() hosts: string[];
  @Input() ips: string[];
  disabledNodes: number[] = [];

  constructor(private router: Router) {}

  ngOnInit(): void {
    [this.nodes, this.edges] = this.structureToGraph(this.structure);
    this.center$.next();
  }

  /**
   * Convert mission structure JSON to nodes and edges
   * @param structure
   */
  structureToGraph(structureJSON: MissionStructure): [Node[], Edge[]] {
    if (structureJSON) {
      const nodes: Node[] = [],
        edges: Edge[] = [];
      // const structureJSON: Structure = JSON.parse(str);

      /**
       * Nodes
       */
      let newNode: Node;

      // Missions
      structureJSON.nodes.missions.forEach((n) => {
        newNode = {
          id: n.id.toString(),
          label: n.name,
          data: { type: 'mission', customColor: '#0f3057', textColor: '#fff' },
        };
        nodes.push(newNode);
      });

      // Services
      structureJSON.nodes.services.forEach((s) => {
        newNode = {
          id: s.id.toString(),
          label: s.name,
          data: { type: 'service', customColor: '#00587a ', textColor: '#fff' },
        };
        nodes.push(newNode);
      });

      // Hosts
      structureJSON.nodes.hosts.forEach((h) => {
        let disabled = false;
        if (this.hosts) {
          disabled = !this.hosts.includes(h.hostname);
        }

        if (this.ips) {
          disabled = this.ips.includes(h.ip);
        }

        if (disabled) {
          this.disabledNodes.push(h.id);
        }

        newNode = {
          id: h.id.toString(),
          label: h.hostname,
          data: { ip: h.ip, type: 'host', customColor: '#008891', textColor: '#fff', disabled },
        };
        nodes.push(newNode);
      });

      // Ands
      structureJSON.nodes.aggregations.and.forEach((a) => {
        newNode = {
          id: a.toString(),
          label: 'AND',
          data: { type: 'and', customColor: '#e7e7de', textColor: '#0f3057' },
        };
        nodes.push(newNode);
      });

      // Ors
      structureJSON.nodes.aggregations.or.forEach((o) => {
        newNode = { id: o.toString(), label: 'OR', data: { type: 'or', customColor: '#e7e7de', textColor: '#0f3057' } };
        nodes.push(newNode);
      });

      /**
       * Edges
       */
      let newEdge: Edge;

      structureJSON.relationships.one_way.forEach((r) => {
        newEdge = { source: r.from.toString(), target: r.to.toString(), label: '' };
        edges.push(newEdge);
      });

      for (let i = 0; i < 4; i++) {
        structureJSON.relationships.one_way.forEach((r) => {
          if (this.disabledNodes.includes(r.to)) {
            const index = nodes.findIndex((node) => node.id === r.from.toString());
            if (nodes[index].label !== 'OR') {
              nodes[index].data.disabled = true;
              this.disabledNodes.push(r.from);
            } else {
              let disableOr = true;
              structureJSON.relationships.one_way
                .filter((rel) => rel.from === r.from)
                .forEach((rel) => {
                  if (!this.disabledNodes.includes(rel.to)) {
                    disableOr = false;
                  }
                });
              if (disableOr) {
                nodes[index].data.disabled = true;
                this.disabledNodes.push(r.from);
              }
            }
          }
        });
      }

      return [nodes, edges];
    } else {
      return [[], []];
    }
  }

  selectNode(node: Node) {
    if (node.data.type === 'mission') {
      this.router.navigateByUrl('/auth/panel/decide/mission/' + node.label);
    }
  }
}
