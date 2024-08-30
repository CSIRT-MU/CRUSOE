import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { GraphInput } from 'src/app/shared/models/graph.model';
import { Node, Edge } from '@swimlane/ngx-graph';
import { environment } from 'src/environments/environment';
import { Observable, throwError } from 'rxjs';
import { AttackedIP, RecommendedIP } from '../models/recommended_ip.model';
import { catchError, map } from 'rxjs/operators';
@Injectable({
  providedIn: 'root',
})
export class RecommenderService {
  private apiUrl = environment.recommenderApi;

  constructor(private http: HttpClient) {}

  getRecommendations(ip: string): Observable<GraphInput> {
    const root_url = `${this.apiUrl}recommender/attacked-host?ip=${ip}`;
    let initial_node: AttackedIP;
    this.http
      .get<AttackedIP>(root_url)
      .pipe(
        map((data) => {
          initial_node = data;
        }),
        catchError((err) => {
          return throwError(err);
        })
      )
      .subscribe();
    const recommended_url = `${this.apiUrl}recommender/recommended-hosts?ip=${ip}`;
    return this.http.get<RecommendedIP[]>(recommended_url).pipe(
      map((data) => {
        const { nodes, edges } = this.convertToGraph(data, ip, initial_node);
        return { nodes, edges };
      })
    );
  }

  public convertToGraph(data: RecommendedIP[], root_ip: string, initial_node: AttackedIP): GraphInput {
    let nodes: Node[] = [];
    let edges: Edge[] = [];

    nodes.push(this.buildInitialNode(root_ip, initial_node));

    for (let i = 0; i < data.length; i++) {
      const current = data[i];
      const node_id = (i + 1).toString();
      nodes.push({
        id: node_id,
        label: current.ip,
        data: {
          ...current,
          customColor: 'red',
        },
      });

      edges.push({ source: '0', target: node_id, label: 'Same ' + current.path_types.join(', ') });
    }
    return { nodes, edges };
  }

  private buildInitialNode(root_ip: string, initial_node: AttackedIP): Node {
    let node: Node = {
      id: '0',
      label: root_ip,
      data: {
        customColor: 'green',
      },
    };

    if (!initial_node) return node;

    node.data = {
      ...initial_node,
      customColor: 'green',
    };

    return node;
  }
}
