import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { MissionComponent } from './mission.component';
import { ActivatedRoute } from '@angular/router';
import { DecideService } from '../decideact.service';

describe('MissionComponent', () => {
  let component: MissionComponent;
  let fixture: ComponentFixture<MissionComponent>;

  beforeEach(
    waitForAsync(() => {
      TestBed.configureTestingModule({
        declarations: [MissionComponent],
        providers: [
          { provide: ActivatedRoute, useValue: { snapshot: { params: name } } },
          {
            provide: DecideService,
            useValue: {
              getMission() {
                return { subscribe: () => {} };
              },
            },
          },
        ],
      }).compileComponents();
    })
  );

  beforeEach(() => {
    fixture = TestBed.createComponent(MissionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
