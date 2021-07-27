#!/usr/bin/python3.6
from neo4jclient.AbsClient import AbstractClient


class NmapClient(AbstractClient):
    def __init__(self, password, **kwargs):
        super().__init__(password=password, **kwargs)

    def create_vertical_scan_cpe(self, nmap_result):
        """
        Create vertical result from nmap_result.

        :param nmap_result: JSON-like form of nmap results
        :return:
        """
        query = "WITH apoc.convert.fromJsonMap($nmap_result) as value " \
                "UNWIND value.data as data " \
                "UNWIND data.cpe as cpe " \
                "WITH cpe, data.ip as ip " \
                "MERGE (ipadd:IP {address: ip}) " \
                "MERGE (softVersion:SoftwareVersion {version: cpe, tag: \'nmap_client\'}) " \
                "MERGE (ipadd)<-[:HAS_ASSIGNED]-(nod:Node) " \
                "MERGE (nod)-[:IS_A]->(host:Host) " \
                "MERGE (softVersion)-[r:ON]->(host)"

        params = {'nmap_result': nmap_result}

        self._run_query(query, **params)

    def create_topology(self, nmap_result):
        """
        Create topology from nmap_result.

        :param nmap_result: JSON-like form of nmap results
        :return:
        """
        query = "WITH apoc.convert.fromJsonMap($nmap_result) as value " \
                "UNWIND value.data as data " \
                "UNWIND data.hops as hops " \
                "MERGE (prev_ip:IP {address:hops.prev_ip}) " \
                "MERGE (prev_node:Node)-[:HAS_ASSIGNED]->(prev_ip)" \
                "MERGE (next_ip:IP {address:hops.next_ip}) " \
                "MERGE (next_node:Node)-[:HAS_ASSIGNED]->(next_ip)" \
                "MERGE (prev_node)-[rel:IS_CONNECTED_TO {hops:hops.hops}]->(next_node) " \
                "ON MATCH SET rel.last_detection = datetime(value.time) " \
                "ON CREATE SET rel.last_detection = datetime(value.time)"

        params = {'nmap_result': nmap_result}

        self._run_query(query, **params)