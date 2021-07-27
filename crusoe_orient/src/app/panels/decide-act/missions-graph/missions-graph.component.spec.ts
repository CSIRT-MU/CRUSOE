import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { MissionsGraphComponent } from './missions-graph.component';
import { RouterTestingModule } from '@angular/router/testing';

describe('MissionsGraphComponent', () => {
  let component: MissionsGraphComponent;
  let fixture: ComponentFixture<MissionsGraphComponent>;

  beforeEach(
    waitForAsync(() => {
      TestBed.configureTestingModule({
        declarations: [MissionsGraphComponent],
        imports: [RouterTestingModule],
      }).compileComponents();
    })
  );

  beforeEach(() => {
    fixture = TestBed.createComponent(MissionsGraphComponent);
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
