import { ComponentFixture, TestBed, waitForAsync } from '@angular/core/testing';

import { PaoComponent } from './pao.component';
import { ActivatedRoute } from '@angular/router';
import { DecideService } from '../../decideact.service';
import { subscribeOn } from 'rxjs/operators';

describe('PaoComponent', () => {
  let component: PaoComponent;
  let fixture: ComponentFixture<PaoComponent>;

  beforeEach(waitForAsync(() => {
    TestBed.configureTestingModule({
      declarations: [PaoComponent],
      providers: [
        { provide: ActivatedRoute, useValue: { snapshot: { params: name } } },
        {
          provide: DecideService,
          useValue: {
            getPaos() {
              return { subscribe: () => {} };
            },
          },
        },
      ],
    }).compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PaoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
