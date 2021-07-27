import { Component, OnInit } from '@angular/core';
import { Node, Edge } from '@swimlane/ngx-graph';
import { Cluster } from 'cluster';
import { DataService } from '../../shared/services/data.service';
import _ from 'lodash';
import { ActivatedRoute } from '@angular/router';
import { Subject } from 'rxjs';

@Component({
  selector: 'app-network-visualization',
  templateUrl: './network-visualization.component.html',
  styleUrls: ['./network-visualization.component.scss'],
})
export class NetworkVisualizationComponent implements OnInit {
  nodes: Node[] = [];
  edges: Edge[] = [];
  clusters: Cluster[];
  loading: boolean;
  error: any;
  selectedNode: Node = { id: '', label: '' };
  ipSearch = '';
  errorMessage = '';
  graphLoading: boolean;
  center$: Subject<any> = new Subject();

  constructor(private dataService: DataService, private route: ActivatedRoute) {
    if (route.snapshot.params && route.snapshot.params.ip) {
      this.ipSearch = route.snapshot.params.ip;
      this.loadGraphData();
    }
  }

  ngOnInit(): void {
    if (this.ipSearch) {
      this.loadGraphData();
    }
  }

  /**
   * Loads graph data from GraphQL API
   */
  loadGraphData() {
    this.graphLoading = true;
    this.errorMessage = '';
    this.selectedNode = { id: '', label: '' };
    this.dataService.getIPNode(this.ipSearch).subscribe(
      (res) => {
        this.edges = res.edges;
        this.nodes = res.nodes;

        if (this.nodes.length === 0 && this.edges.length === 0) {
          this.errorMessage = 'Empty result.';
        }

        this.updateChart();
        this.graphLoading = false;
      },
      (error) => {
        this.edges = [];
        this.nodes = [];
        this.errorMessage = error;
        this.graphLoading = false;
      }
    );
  }

  /**
   * This function is called when a user clicks on graph node
   * @param node selected node
   */
  selectNode(node: Node) {
    this.selectedNode = node;
  }

  /**
   * Returns node attributes of type string ignoring attributes such as color, labelname
   * @param node
   */
  public getNodeAttributes(node: Node) {
    const attr = { ...node.data };
    delete attr.color;
    delete attr.customColor;
    delete attr.type;
    delete attr.labelName;
    return Object.entries(attr).filter((a) => typeof a[1] === 'string' || typeof a[1] === 'number');
  }

  public getLabel(node: Node) {
    return this.dataService.getLabelOfGraphNode(node);
  }

  public expandNode(node: Node) {
    this.dataService.getNodeNeighbours(node).subscribe(
      (res) => {
        this.edges = _.unionBy(this.edges, res.edges, (e) => [e.source, e.target, e.label].join());
        this.nodes = _.unionBy(this.nodes, res.nodes, (n) => n.id);

        if (this.nodes.length === 0 && this.edges.length === 0) {
          this.errorMessage = 'Empty result.';
        }

        this.graphLoading = false;
      },
      (error) => {
        this.edges = [];
        this.nodes = [];
        this.errorMessage = error;
        this.updateChart();
        this.graphLoading = false;
      }
    );
  }

  updateChart() {
    this.center$.next(true);
  }
}
