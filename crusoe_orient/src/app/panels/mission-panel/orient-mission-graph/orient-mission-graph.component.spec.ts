import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { OrientMissionGraphComponent } from './orient-mission-graph.component';
import { RouterTestingModule } from '@angular/router/testing';

describe('OrientMissionGraphComponent', () => {
  let component: OrientMissionGraphComponent;
  let fixture: ComponentFixture<OrientMissionGraphComponent>;

  beforeEach(
    waitForAsync(() => {
      TestBed.configureTestingModule({
        declarations: [OrientMissionGraphComponent],
        imports: [RouterTestingModule],
      }).compileComponents();
    })
  );

  beforeEach(() => {
    fixture = TestBed.createComponent(OrientMissionGraphComponent);
    component = fixture.componentInstance;
    component.structure = {
      nodes: { missions: [], hosts: [], aggregations: { and: [], or: [] }, services: [] },
      relationships: { two_way: [], one_way: [], supports: [], has_identity: [] },
    };
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
