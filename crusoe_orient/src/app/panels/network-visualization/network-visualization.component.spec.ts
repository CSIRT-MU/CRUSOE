import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { NetworkVisualizationComponent } from './network-visualization.component';
import { DataService } from '../../shared/services/data.service';
import { of, throwError, from } from 'rxjs';
import { ActivatedRoute } from '@angular/router';

describe('NetworkVisualizationComponent', () => {
  let component: NetworkVisualizationComponent;
  let fixture: ComponentFixture<NetworkVisualizationComponent>;
  const dataServiceMock = jasmine.createSpyObj('DataService', ['getIPNode']);
  dataServiceMock.getIPNode.and.returnValue(throwError('Error'));

  beforeEach(
    waitForAsync(() => {
      TestBed.configureTestingModule({
        declarations: [NetworkVisualizationComponent],
        providers: [
          { provide: DataService, useValue: dataServiceMock },
          {
            provide: ActivatedRoute,
            useValue: {
              snapshot: {
                params: {
                  ip: '8.8.8.8',
                },
              },
            },
          },
        ],
      }).compileComponents();
    })
  );

  beforeEach(() => {
    fixture = TestBed.createComponent(NetworkVisualizationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
