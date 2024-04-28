import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Node, Edge } from '@swimlane/ngx-graph';
import { Cluster } from 'cluster';
import { Subject } from 'rxjs';
import _ from 'lodash';
import { RecommenderService } from 'src/app/shared/services/recommender.service';
import { NoDeprecatedCustomRule } from 'graphql';
import { MatTableModule } from '@angular/material/table';

@Component({
  selector: 'app-recommender-system-visualization-component',
  templateUrl: './recommender-system-visualization.component.html',
  styleUrls: ['./recommender-system-visualization.component.scss'],
})
export class RecommenderSystemVisualizationComponent implements OnInit {
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
  displayedColumns: string[] = [
    'ip',
    'domains',
    'contacts',
    'os',
    'antivirus',
    'cve_count',
    'event_count',
    'risk',
    'distance',
  ];

  constructor(private recommenderService: RecommenderService, private route: ActivatedRoute) {
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
    this.recommenderService.getRecommendations(this.ipSearch).subscribe(
      (res) => {
        console.log(res);
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
        this.errorMessage = error.error.error.message;
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

  public isIterable(value: any): boolean {
    return Array.isArray(value);
  }

  /**
   * Returns node attributes of type string ignoring attributes such as color, labelname
   * @param node
   */
  public getNodeAttributes(node: Node) {
    const attr = {
      contacts: node.data.contacts,
      domains: node.data.domains,
      os: this.joinDict(node.data.os),
      antivirus: this.joinDict(node.data.antivirus),
      security_event_count: [node.data.security_event_count],
    };
    return Object.entries(attr);
  }

  private joinDict(dict): string[] {
    if (dict === null) {
      return ['*:*:*'];
    }
    const values = Object.values(dict);
    return [values.join(':')];
  }

  private handleUndefined(value: any): string {
    return value !== undefined ? value : ' ';
  }
  /*
  public getLabel(node: Node) {
    return this.recommenderService.getLabelOfGraphNode(node);
  }

  public expandNode(node: Node) {
    this.recommenderService.getNodeNeighbours(node).subscribe(
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
*/
  updateChart() {
    this.center$.next(true);
  }
}
