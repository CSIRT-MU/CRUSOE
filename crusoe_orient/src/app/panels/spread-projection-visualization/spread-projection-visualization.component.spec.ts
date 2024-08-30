import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SpreadProjectionVisualizationComponent } from './spread-projection-visualization.component';

describe('SpreadProjectionVisualizationComponent', () => {
  let component: SpreadProjectionVisualizationComponent;
  let fixture: ComponentFixture<SpreadProjectionVisualizationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [SpreadProjectionVisualizationComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SpreadProjectionVisualizationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
