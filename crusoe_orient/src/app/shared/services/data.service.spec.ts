import { TestBed } from '@angular/core/testing';

import { DataService } from './data.service';
import { ApolloTestingController, ApolloTestingModule, APOLLO_TESTING_CACHE } from 'apollo-angular/testing';
import { gql } from 'apollo-angular';
import { InMemoryCache } from '@apollo/client/core';
import { addTypenameToDocument } from '@apollo/client/utilities';
import { TEST_IP_DATA, TEST_NEIGHBOUR_DATA, TEST_NEIGHBOUR_NODE } from './test.data';
// import {InMemoryCache} from 'apollo-cache-inmemory';

describe('DataService', () => {
  let service: DataService;
  let controller: ApolloTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ApolloTestingModule],
      providers: [
        {
          provide: APOLLO_TESTING_CACHE,
          useValue: new InMemoryCache({ addTypename: true }),
        },
      ],
    });

    controller = TestBed.inject(ApolloTestingController);
    service = TestBed.inject(DataService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should return IP node', () => {
    service.getIPNode('127.0.0.1').subscribe((data) => {
      expect(data.edges.length).toBeGreaterThan(0);
      expect(data.nodes[0].label).toEqual('127.0.0.1');
    });

    const op = controller.expectOne(
      addTypenameToDocument(gql`
    {
      IP(address: "127.0.0.1") {
        ${service.getAttributesOfType('IP')}
      }
    }
  `)
    );

    op.flush(TEST_IP_DATA);
  });

  it('should return node neighbours', () => {
    service.getNodeNeighbours(TEST_NEIGHBOUR_NODE).subscribe((data) => {
      console.log('daticka', data);
      expect(data.edges.length).toBeGreaterThan(0);
      expect(data.nodes[1].data.type).toEqual('DomainName');
    });

    const op = controller.expectOne(
      addTypenameToDocument(gql`
      {
        IP(_id: "12345") {
          ${service.getAttributesOfType('IP')}
        }
      }
    `)
    );

    op.flush(TEST_NEIGHBOUR_DATA);
  });

  afterEach(() => {
    controller.verify();
  });
});
