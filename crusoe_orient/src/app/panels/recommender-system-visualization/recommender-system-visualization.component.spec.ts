import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RecommenderSystemVisualizationComponent } from './recommender-system-visualization.component';

describe('RecommenderSystemVisualizationComponentComponent', () => {
  let component: RecommenderSystemVisualizationComponent;
  let fixture: ComponentFixture<RecommenderSystemVisualizationComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [RecommenderSystemVisualizationComponent],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(RecommenderSystemVisualizationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
