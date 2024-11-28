/**
 * Components
 * */
import { DecideActComponent } from 'src/app/panels/decide-act/decideact.component';
import { PanelOverviewComponent } from 'src/app/panels/panel-overview/panel-overview.component';
import { AuthSectionComponent } from './shared/components/auth-section/auth-section.component';
import { LoginScreenComponent } from './authentication/components/login-screen/login-screen.component';
import { PanelComponent } from 'src/app/shared//components/panel/panel.component';
import { NotFoundComponent } from 'src/app/shared/components/not-found/not-found.component';
import { TaskManagerComponent } from 'src/app//panels/task-manager/task-manager.component';
import { WorkerComponent } from 'src/app/panels/task-manager/worker/worker.component';
import { TaskComponent } from 'src/app/panels/task-manager/task/task.component';
import { PaoComponent } from 'src/app/panels/decide-act/pao/pao/pao.component';
import { MissionComponent } from 'src/app/panels/decide-act/mission/mission.component';
import { NetworkVisualizationComponent } from './panels/network-visualization/network-visualization.component';
import { RecommenderSystemVisualizationComponent } from './panels/recommender-system-visualization/recommender-system-visualization.component';
import { SpreadProjectionVisualizationComponent } from './panels/spread-projection-visualization/spread-projection-visualization.component';
import { VulnerabilityComponent } from './panels/vulnerability/vulnerability.component';
import { ConfigurationComponent } from 'src/app/panels/decide-act/configuration/configuration.component';
import { MyAccountComponent } from './panels/my-account/my-account.component';

/**
 * Modules and services
 */
import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AuthGuard } from 'src/app/authentication/services/auth-guard.service';
import { AuthGuardNegative } from './authentication/services/auth-guard-negative.service';
import { MissionPanelComponent } from './panels/mission-panel/mission-panel.component';

// PANELS
export const panelGroups = [{ name: 'Observe'}, { name: 'Orient'}, {name: 'Decide'}, {name: 'Act'}];

// Add all new panels here
export const panels = [
  {
    data: { name: 'Task Manager', panelGroup: panelGroups[0] },
    path: 'task-manager',
    component: TaskManagerComponent,
    canActivate: [AuthGuard],
  },
  {
    data: { name: 'Network Nodes', panelGroup: panelGroups[1] },
    path: 'network-visualization',
    component: NetworkVisualizationComponent,
    canActivate: [AuthGuard],
  },
  {
    data: { name: 'Vulnerabilities', panelGroup: panelGroups[1] },
    path: 'vulnerability',
    component: VulnerabilityComponent,
    canActivate: [AuthGuard],
  },
  {
    data: { name: 'Missions', panelGroup: panelGroups[1] },
    path: 'mission-panel',
    component: MissionPanelComponent,
    canActivate: [AuthGuard],
  },
  {
    data: { name: 'Recommender System', panelGroup: panelGroups[2] },
    path: 'recommender-system-visualization',
    component: RecommenderSystemVisualizationComponent,
    canActivate: [AuthGuard],
  },
  {
    data: { name: 'Attack Spread Projection', panelGroup: panelGroups[2] },
    path: 'spread-projection-visualization',
    component: SpreadProjectionVisualizationComponent,
    canActivate: [AuthGuard],
  },
  {
    data: { name: 'Decide & Act', panelGroup: panelGroups[3] },
    path: 'decide',
    component: DecideActComponent,
    canActivate: [AuthGuard],
  },
];

export const panelsText = panels.map(({ data, path }) => ({ data, path }));

const routes: Routes = [
  { path: 'login', component: LoginScreenComponent, canActivate: [AuthGuardNegative] },
  {
    path: 'auth',
    component: AuthSectionComponent,
    canActivate: [AuthGuard],
    children: [
      { path: '', pathMatch: 'full', redirectTo: 'panel/overview' },
      { path: 'profile', component: MyAccountComponent, canActivate: [AuthGuard] },
      {
        path: 'panel',
        component: PanelComponent,
        canActivate: [AuthGuard],
        children: [
          {
            data: { name: 'Overview', panelGroup: null, panelsText },
            path: 'overview',
            component: PanelOverviewComponent,
            canActivate: [AuthGuard],
          },
          {
            data: { type: 'Task Manager / Workers' },
            path: 'task-manager/workers/:id',
            component: WorkerComponent,
            canActivate: [AuthGuard],
          },
          {
            data: { type: 'Task Manager / Tasks' },
            path: 'task-manager/tasks/:id',
            component: TaskComponent,
            canActivate: [AuthGuard],
          },
          ...panels,
          {
            data: { type: 'Decide/Act / PAO' },
            path: 'decide/pao/:name',
            component: PaoComponent,
            canActivate: [AuthGuard],
          },
          {
            data: { type: 'Decide/Act / Mission' },
            path: 'decide/mission/:name',
            component: MissionComponent,
            canActivate: [AuthGuard],
          },
          {
            data: { type: 'Decide/Act / Configuration' },
            path: 'decide/configuration/:missionName/:id',
            component: ConfigurationComponent,
            canActivate: [AuthGuard],
          },
          {
            data: { name: 'Network Visualization', panelGroup: panelGroups[0] },
            path: 'network-visualization/:ip',
            component: NetworkVisualizationComponent,
            canActivate: [AuthGuard],
          },
          {
            data: { name: 'Recommender Visualization', panelGroup: panelGroups[0] },
            path: 'recommender-system-visualization/:ip',
            component: RecommenderSystemVisualizationComponent,
            canActivate: [AuthGuard],
          },
          {
            data: { name: 'Recommender Visualization', panelGroup: panelGroups[0] },
            path: 'spread-projection-visualization/:ip',
            component: SpreadProjectionVisualizationComponent,
            canActivate: [AuthGuard],
          },
        ],
      },
    ],
  },
  {
    path: '',
    redirectTo: 'login',
    pathMatch: 'full',
  },
  { path: '**', component: NotFoundComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { initialNavigation: 'disabled', relativeLinkResolution: 'legacy' })],
  exports: [RouterModule],
})
export class AppRoutingModule {}
