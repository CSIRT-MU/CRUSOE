from neo4j import GraphDatabase
from Model.host import Host
from Model.network_service import NetworkService
from Model.software_component import SoftwareComponent
from ipaddress import ip_address
import logging
from neo4j.exceptions import ServiceUnavailable


class DatabaseConnection:
    def __init__(self, url, user, password):
        self.driver = GraphDatabase.driver(url, auth=(user, password))

    def close(self):
        """
        Closes connection with database.
        :return: None
        """
        self.driver.close()

    def get_host_by_domain(self, domain):
        """
        Finds host in the database by its domain address and initialize its
        properties. Throws ValueError when given domain doesn't exist in
        database.
        :param domain: Domain name as string
        :return: Host object
        """

        with self.driver.session() as session:
            result = session.read_transaction(self._get_ip, domain)

            # Domain doesn't exist in database
            if not result:
                raise ValueError("Given domain was not resolved to any IP")

            # Create new IP address object
            ip_str = ip_address(result[0]["address"])

        return self.get_host_by_ip(ip_str)

    def get_host_by_ip(self, ip):
        """
        Finds host in the database by its IP address and initialize its
        properties. Throws ValueError when given IP doesn't exist in database.
        :param ip: IP address object
        :return: Host object
        """

        # Get IP as string
        ip_str = str(ip)

        with self.driver.session() as session:
            result = session.read_transaction(self._get_host_by_ip,
                                              ip_str)

            # IP doesn't exist in database
            if not result:
                raise ValueError("Given IP was not found in database.")

            domains = result[0]["domain_list"]
            os = result[0]["os"]

        # Create new host
        new_host = Host(ip, domains, os)

        # Initialize software components and network services lists
        new_host.software_components = self.get_software_components(ip_str)
        new_host.network_services = self.get_network_services(ip_str)

        return new_host

    def get_network_services(self, ip):
        """
        Loads
        :param ip:
        :return:
        """
        with self.driver.session() as session:
            result = session.read_transaction(self._get_network_services, ip)

            services = []
            for row in result:
                service = NetworkService(row["port"],
                                         row["protocol"],
                                         row["service"])
                services.append(service)
            return services

    def get_software_components(self, ip):
        """

        :param ip:
        :return:
        """
        with self.driver.session() as session:

            result = session.read_transaction(
                self._get_software_components, ip)

            sw_components = []
            for row in result:
                sw = SoftwareComponent(row["tag"],
                                       row["version"])
                sw_components.append(sw)
            return sw_components

    @staticmethod
    def _get_ip(tx, domain):
        query = (
            "MATCH (ip:IP)-[:RESOLVES_TO]->(domain:DomainName) "
            "WHERE $domain IN domain.domain_name "
            "RETURN ip"
        )
        result = tx.run(query, domain=domain)
        return [row["ip"] for row in result]

    @staticmethod
    def _check_ip(tx, ip):
        query = (
            "MATCH (ip:IP) "
            "WHERE ip.address = $ip "
            "RETURN ip"
        )
        result = tx.run(query, ip=ip)
        return [row["ip"] for row in result]

    @staticmethod
    def _get_host_by_ip(tx, ip):
        query = (
            "MATCH (node:Node)-[:HAS_ASSIGNED]->(ip:IP) "  # Find IP
            "WHERE ip.address = $ip "
            "MATCH (node)-[:IS_A]->(host:Host) "
            "OPTIONAL MATCH (sw:SoftwareVersion)-[rel:ON]->(host) "
            "WHERE sw.tag = \"os_component\" "
            "WITH sw AS os, ip "
            "ORDER BY datetime(sw.end) DESC "  # Get latest running OS
            "LIMIT 1 "
            # Get domains
            "OPTIONAL MATCH (ip:IP)-[:RESOLVES_TO]->(domain:DomainName) "
            # Reduce all domain names in one list
            "RETURN REDUCE(s = [], domain_name IN COLLECT(domain.domain_name) "  
            "| s + domain_name) AS domain_list, os.version AS os"
        )
        result = tx.run(query, ip=ip)

        return [row for row in result]

    @staticmethod
    def _get_network_services(tx, ip):
        query = (
            "MATCH (node:Node)-[:HAS_ASSIGNED]->(ip:IP) "
            "WHERE ip.address = $ip "
            "MATCH (node)-[:IS_A]->(host:Host) "
            "MATCH (service:NetworkService)-[:ON]->(host) "
            "RETURN service"
        )
        result = tx.run(query, ip=ip)
        return [row["service"] for row in result]

    @staticmethod
    def _get_software_components(tx, ip):
        query = (
            "MATCH (node:Node)-[:HAS_ASSIGNED]->(ip:IP) "
            "WHERE ip.address = $ip "
            "MATCH (node)-[:IS_A]->(host:Host) "
            "MATCH (software: SoftwareVersion)-[:ON]->(host) "
            "WHERE software.tag <> 'os_component' "
            "RETURN software"
        )
        result = tx.run(query, ip=ip)
        return [row["software"] for row in result]
