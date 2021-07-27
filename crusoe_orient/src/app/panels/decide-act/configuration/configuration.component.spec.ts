import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ConfigurationComponent } from './configuration.component';
import { ActivatedRoute } from '@angular/router';
import { of } from 'rxjs';
import { DecideService } from '../decideact.service';

describe('ConfigurationComponent', () => {
  let component: ConfigurationComponent;
  let fixture: ComponentFixture<ConfigurationComponent>;

  beforeEach(async () => {
    const decideServiceMock = {
      getMissionConfiguration: function () {
        return of(5);
      },
      getConfigurationHosts: function () {
        return of(5);
      },
      getMission: function () {
        return of({ structure: '{}' });
      },
    };

    await TestBed.configureTestingModule({
      declarations: [ConfigurationComponent],
      providers: [
        { provide: ActivatedRoute, useValue: { snapshot: { params: [] } } },
        { provide: DecideService, useValue: decideServiceMock },
      ],
    }).compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ConfigurationComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
