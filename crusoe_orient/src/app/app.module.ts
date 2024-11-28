/**
 * Authentication
 */
import { AuthService } from './authentication/services/auth.service';
import { OAuthModule, OAuthStorage } from 'angular-oauth2-oidc';
import { AuthGuardNegative } from './authentication/services/auth-guard-negative.service';
import { AuthGuard } from './authentication/services/auth-guard.service';
import { ApiInterceptor } from './shared/interceptors/api.interceptor';

/**
 * Angular Material
 */
import { MatTabsModule } from '@angular/material/tabs';
import { MatSnackBarModule } from '@angular/material/snack-bar';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatTableModule } from '@angular/material/table';
import { MatSortModule } from '@angular/material/sort';
import { MatPaginatorModule } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatCheckboxModule } from '@angular/material/checkbox';

/**
 * Panels
 */
// Panel overview
import { PanelOverviewComponent } from './panels/panel-overview/panel-overview.component';

// Task Manager
import { TaskManagerComponent } from './panels/task-manager/task-manager.component';
import { WorkerComponent } from './panels/task-manager/worker/worker.component';
import { TaskComponent } from './panels/task-manager/task/task.component';

// Missions
import { MissionsPanelComponent } from './panels/missions-panel/missions-panel.component';

// Decide-Act
import { DecideActComponent } from './panels/decide-act/decideact.component';

// Network Visualization
import { NetworkVisualizationComponent } from './panels/network-visualization/network-visualization.component';

// Custom panel
import { MissionPanelComponent } from './panels/mission-panel/mission-panel.component';

// Recommender System Visualization
import { RecommenderSystemVisualizationComponent } from './panels/recommender-system-visualization/recommender-system-visualization.component';

// Spread Projection Visualization
import { SpreadProjectionVisualizationComponent } from './panels/spread-projection-visualization/spread-projection-visualization.component';

// Vulnerability
import { VulnerabilityComponent } from './panels/vulnerability/vulnerability.component';

// My Account
import { MyAccountComponent } from './panels/my-account/my-account.component';

/**
 * Other components
 */
import { AppComponent } from './app.component';
import { SidebarComponent } from './shared/components/sidebar/sidebar.component';
import { AuthSectionComponent } from './shared/components/auth-section/auth-section.component';
import { MissionsGraphComponent } from './panels/decide-act/missions-graph/missions-graph.component';
import { OrientMissionGraphComponent } from './panels/mission-panel/orient-mission-graph/orient-mission-graph.component';
import { ConfigurationComponent } from './panels/decide-act/configuration/configuration.component';
import { PanelComponent } from './shared/components/panel/panel.component';
import { NotFoundComponent } from './shared/components/not-found/not-found.component';
import { MissionComponent } from './panels/decide-act/mission/mission.component';
import { PaoComponent } from './panels/decide-act/pao/pao/pao.component';
import { LoginScreenComponent } from './authentication/components/login-screen/login-screen.component';
import { LogoutComponent } from './authentication/components/logout/logout.component';
import { NavbarComponent } from './shared/components/navbar/navbar.component';

// Modules

import { NgModule } from '@angular/core';
import { BrowserModule, Title } from '@angular/platform-browser';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
// Routing
import { AppRoutingModule } from './app-routing.module';

// Ngx-charts, Ngx-graph
import { NgxChartsModule } from '@swimlane/ngx-charts';
import { NgxGraphModule } from '@swimlane/ngx-graph';

// GraphQL module
import { GraphQLModule } from './shared/services/graphql.module';
import { MatSelectModule } from '@angular/material/select';

@NgModule({
  declarations: [
    AppComponent,
    SidebarComponent,
    NotFoundComponent,
    PanelComponent,
    SidebarComponent,
    LoginScreenComponent,
    MyAccountComponent,
    LogoutComponent,
    NavbarComponent,
    AuthSectionComponent,
    PanelOverviewComponent,
    TaskManagerComponent,
    DecideActComponent,
    WorkerComponent,
    TaskComponent,
    PaoComponent,
    MissionComponent,
    MissionsGraphComponent,
    OrientMissionGraphComponent,
    ConfigurationComponent,
    NetworkVisualizationComponent,
    MissionPanelComponent,
    VulnerabilityComponent,
    RecommenderSystemVisualizationComponent,
    SpreadProjectionVisualizationComponent,
  ],
  imports: [
    BrowserModule,
    MatProgressSpinnerModule,
    BrowserAnimationsModule,
    MatTabsModule,
    MatSnackBarModule,
    MatPaginatorModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
    AppRoutingModule,
    OAuthModule.forRoot({
      resourceServer: {
        allowedUrls: ['https://oidc.muni.cz/oidc/userinfo', 'http://localhost:8000/api/panels'],
        sendAccessToken: true,
      },
    }),
    NgxChartsModule,
    MatProgressSpinnerModule,
    MatTabsModule,
    MatSnackBarModule,
    GraphQLModule,
    NgxGraphModule,
    MatCardModule,
    MatIconModule,
    MatMenuModule,
    MatFormFieldModule,
    MatTableModule,
    MatSortModule,
    MatButtonModule,
    FormsModule,
    MatInputModule,
    MatSelectModule,

    MatCheckboxModule,
  ],
  providers: [
    {
      provide: OAuthStorage,
      useValue: localStorage,
    },
    AuthGuard,
    AuthGuardNegative,
    AuthService,
    Title,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: ApiInterceptor,
      multi: true,
    },
  ],
  bootstrap: [AppComponent],
})
export class AppModule {}
