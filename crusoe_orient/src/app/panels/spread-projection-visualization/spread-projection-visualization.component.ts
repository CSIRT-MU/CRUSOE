import { Component, OnInit } from '@angular/core';
import { Node, Edge } from '@swimlane/ngx-graph';
import { Cluster } from 'cluster';
import { DataService } from '../../shared/services/data.service';
import _ from 'lodash';
import { ActivatedRoute } from '@angular/router';
import { Subject } from 'rxjs';
import { Subnet } from 'src/app/shared/models/subnet.model';

@Component({
  selector: 'app-spread-projection-visualization-component',
  templateUrl: './spread-projection-visualization.component.html',
  styleUrls: ['./spread-projection-visualization.component.scss'],
})
export class SpreadProjectionVisualizationComponent implements OnInit {
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
  subnets: Subnet[] = [];
  selectedSubnet = '';
  missions: string[] = [];
  selectedMission = '';

  constructor(private dataService: DataService, private route: ActivatedRoute) {
    if (route.snapshot.params && route.snapshot.params.ip) {
      this.ipSearch = route.snapshot.params.ip;
      this.loadGraphData();
    }
  }

  ngOnInit(): void {
    this.dataService.getTraversalParameters().subscribe(
      (res) => {
        this.subnets = res.subnets; // Store the array in the component
        this.missions = res.missions;
      },
      (error) => {
        this.errorMessage = error.message || 'Error fetching subnets'; // Handle errors
      }
    );
  }

  /**
   * Loads graph data from GraphQL API
   */
  async loadGraphData() {
    console.log(this.selectedSubnet);
    console.log(this.selectedMission);
    if (this.selectedSubnet && this.selectedMission) {
      this.errorMessage = "Can't select both Mission and a Subnet.";
      return;
    }
    this.graphLoading = true;
    this.errorMessage = '';
    this.selectedNode = { id: '', label: '' };
    let ipSubnet = '';
    if (!this.selectedSubnet && !this.selectedMission) {
      try {
        ipSubnet = await this.dataService.getIPSubnet(this.ipSearch).toPromise();
      } catch (error) {
        this.errorMessage = 'No subnet associated with IP.';
        this.graphLoading = false;
      }
      if (ipSubnet === '') return;
    }
    this.dataService.getTraversalBase(this.ipSearch, this.selectedSubnet || ipSubnet, this.selectedMission).subscribe(
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
    return Object.entries(node.data.similarity);
  }

  public getLabel(node: Node) {
    return this.dataService.getLabelOfGraphNode(node);
  }

  updateChart() {
    this.center$.next(true);
  }
}
