#!/usr/bin/python3.6
"""
Module contains temporary cypher queries used in tests.
"""

from neo4j import GraphDatabase, basic_auth
from neo4jclient.CveConnectorClient import CVEConnectorClient
from neo4jclient.RESTClient import RESTClient


class TestClient(CVEConnectorClient, RESTClient):
    """
    Class for passing queries utilized in tests to database.
    """
    def __init__(self, bolt="bolt://localhost:7687", user="neo4j", password=None, lifetime=120):
        self._user = user
        self._driver = GraphDatabase.driver(bolt, auth=basic_auth(user, password),
                                            max_connection_lifetime=lifetime, encrypted=True)
        super().__init__(driver=self._driver, password=password)

    def delete_all(self):
        """
        Deletes all nodes and relationships from database.
        !!!CAUTION!!! Do not use with a database containing important data.

        :return: None
        """
        self._run_query("MATCH (n) WITH n LIMIT 100 DETACH DELETE n")

    def create_software_version(self, version):
        """
        Creates software version with specified 'version' parameter.

        :param version: version of software resource
        :return: None
        """
        self._run_query("MERGE (ver:SoftwareVersion {version: $version})",
                        **{'version': version})

    def add_vulnerability_to_resource_version(self, resource_version, vul_description):
        """
        Creates relationship between vulnerability and software version.

        :param resource_version: version of resource
        :param vul_description: description of vulnerability
        :return: None
        """
        self._run_query("MATCH (s:SoftwareVersion {version: $version}) "
                        "MERGE (vul:Vulnerability {description: $description})-[:IN]->(s)",
                        **{'version': resource_version, 'description': vul_description})

    def create_new_host(self, hostname, contact):
        """
        Create new node of type host.

        :param hostname: name of host
        :param contact: contact on host
        :return: None
        """
        self._run_query("MERGE (host:Host {hostname: $hostname, contact: $contact})",
                        **{'hostname': hostname, 'contact': contact})

    def add_ip_to_host(self, hostname, ip_address):
        """
        Creates relationship between IP and host.

        :param hostname: name of host
        :param ip_address: IP address
        :return: None
        """
        self._run_query(
            "MATCH (h:Host {hostname: $hostname}) "
            "MERGE (h)<-[:IS_A]-(:Node)-[:HAS_ASSIGNED]->(ip:IP {address: $ip_address})",
            **{'hostname': hostname, 'ip_address': ip_address})

    def create_subnet(self, subnet_range, contact=None):
        """
        Creates node of type: subnet.

        :param subnet_range: range of IPs for a subnet
        :param contact: Contact responsible for given subnet.
        :return: None
        """
        self._run_query("CREATE (sub:Subnet {range: $range, contact: $contact})",
                        **{'range': subnet_range, 'contact': contact})

    def create_relationship_between_IP_and_subnet(self, ip_address, subnet_range):
        """
        Create relationship of type: "PART_OF" between IP and subnet.

        :param ip_address: IP address
        :param subnet_range: range of IPs for a subnet
        :return: None
        """
        self._run_query("MATCH (ip:IP), (sub:Subnet)\
                                WHERE ip.address = $ip_address AND sub.range = $range\
                                MERGE (ip)-[r:PART_OF]->(sub)",
                        **{'ip_address': ip_address, 'range': subnet_range})

    def set_relationship_between_comp_and_host(self, comp_name, hostname, port, protocol,
                                               software):
        """
        This function sets port, protocol and software for the relationship between component
        and host.

        :param comp_name: name of component
        :param hostname: name of host
        :param port: port on which the software runs
        :param protocol: name of protocol
        :param software: name of software in the form of part of CPE
        :return: None
        """
        self._run_query(
            "MATCH (comp:Component {name: $comp_name})-[r:PROVIDED_BY]->(host:Host "
            "{hostname: $hostname}) "
            "SET r.port = $port, r.protocol = $protocol, r.sw = $software",
            **{'comp_name': comp_name, 'hostname': hostname, 'port': port, 'protocol': protocol,
               'software': software})

    def create_relationship_between_software_version_and_host_empty(self, version, hostname):
        """
        Creates relationship between :SoftwareVersion and :Host without any properties.

        :param version: software version (CPE)
        :param hostname: name of host
        :return: None
        """
        self._run_query("MATCH (v:SoftwareVersion), (host:Host) \
                         WHERE v.version = $version AND host.hostname = $hostname \
                         MERGE (v)-[:ON]->(host)",
                        **{'version': version, 'hostname': hostname})

    def create_relationship_between_software_version_and_host(self, version, hostname, port,
                                                              protocol):
        """
        Creates relationship between :SoftwareVersion and :Host with properties port
        and protocol being set.

        :param version: software version
        :param hostname: name of host
        :param port: port on which the software runs
        :param protocol: name of protocol
        :return: None
        """
        self._run_query("MATCH (v:SoftwareVersion), (host:Host) \
                         WHERE v.version = $version AND host.hostname = $hostname \
                         MERGE (v)-[:ON {port: $port, protocol: $protocol}]->(host)",
                        **{'version': version, 'hostname': hostname, 'port': port,
                           'protocol': protocol})

    def set_ip_as_compromised(self, ip_address):
        """
        Set flag 'compromised' to True.

        :param ip_address: IP address
        :return: None
        """
        self._run_query("MATCH (ip:IP {address: $ip_address}) SET ip.compromised = True",
                        **{'ip_address': ip_address})
