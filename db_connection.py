from neo4j import GraphDatabase
from Model.host import Host, HostWithScore
from Model.network_service import NetworkService
from Model.software_component import SoftwareComponent
from ipaddress import ip_address
from Model.path_type import PathType
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
            result = session.read_transaction(self._get_ip_query, domain)

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
            result = session.read_transaction(self._get_host_by_ip_query,
                                              ip_str)

            # IP doesn't exist in database
            if not result:
                return
                # raise ValueError("Given IP was not found in database.")

            domains = result[0]["domain_list"]
            os_cpe = result[0]["os"]

            # Create new host
            new_host = Host(ip, domains, os_cpe)

            # Initialize software components and network services lists
            new_host.software_components = self._get_software_components(
                ip_str,
                session)
            new_host.network_services = self._get_network_services(ip_str,
                                                                   session)

        return new_host

    def find_close_hosts(self, ip, max_distance):
        """

        :param ip:
        :param max_distance:
        :return:
        """
        with self.driver.session() as session:
            result = session.read_transaction(self._find_close_hosts_query,
                                              ip, max_distance)

            result_list = []

            for row in result:
                try:
                    ip = ip_address(row["ip"])
                except ValueError:
                    # log
                    continue

                path_types = {"subnet": PathType.Subnet,
                              "organization": PathType.Organization,
                              "contact": PathType.Contact}

                new_host = HostWithScore(ip,
                                         row["domains"],
                                         row["os"],
                                         row["vulner_count"],
                                         row["event_count"],
                                         path_types[row["path_type"]],
                                         row["distance"])

                new_host.network_services = self._get_network_services(str(ip),
                                                                       session)
                new_host.software_components = \
                    self._get_software_components(str(ip), session)

                result_list.append(new_host)

            return result_list

    def _get_network_services(self, ip, session):
        """
        Finds network services in database which runs on a host with given IP.
        :param ip: Host's IP address
        :return: List of network_service objects
        """

        result = session.read_transaction(self._get_network_services_query, ip)

        services = []
        for row in result:
            service = NetworkService(row["port"],
                                     row["protocol"],
                                     row["service"])
            services.append(service)
        return services

    def _get_software_components(self, ip, session):
        """
        Finds software (except operation system components) in database which
        runs on a host with given IP.
        :param ip: Host's IP address
        :return: List of network_service objects
        """
        result = session.read_transaction(self._get_software_components_query,
                                          ip)

        sw_components = []
        for row in result:
            sw = SoftwareComponent(row["tag"],
                                   row["version"])
            sw_components.append(sw)
        return sw_components

    @staticmethod
    def _get_ip_query(tx, domain):
        query = (
            "MATCH (ip:IP)-[:RESOLVES_TO]->(domain:DomainName) "
            "WHERE $domain IN domain.domain_name "
            "RETURN ip"
        )
        result = tx.run(query, domain=domain)
        return [row["ip"] for row in result]

    @staticmethod
    def _get_host_by_ip_query(tx, ip):
        query = (
            "MATCH (node:Node)-[:HAS_ASSIGNED]->(ip:IP) "
            "WHERE ip.address = $ip "
            "MATCH (node)-[:IS_A]->(host:Host) "
            "OPTIONAL MATCH (vulner:Vulnerability)-[:IN]->(sw:SoftwareVersion)-[rel:ON]->(host) "
            "OPTIONAL MATCH (sw) "
            "WHERE sw.tag = \"os_component\" "
            "WITH sw AS os, ip "
            "ORDER BY datetime(sw.end) DESC "
            "LIMIT 1 "
            "OPTIONAL MATCH (ip:IP)-[:RESOLVES_TO]->(domain:DomainName) "
            "RETURN ip.address, "
            "REDUCE(s = [], domain_name IN COLLECT(domain.domain_name) | s + domain_name) AS domain_list, "
            "os.version AS os "
        )

        result = tx.run(query, ip=ip)

        return [row for row in result]

    @staticmethod
    def _get_network_services_query(tx, ip):
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
    def _get_software_components_query(tx, ip):
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

    @staticmethod
    def _find_close_hosts_query(tx, ip, max_distance):
        query = (
            # Traverse from given IP address node
            "CALL traverse.findCloseHosts($ip, $max_distance) "
            "YIELD ip, distance, path_type "
            "MATCH (host:Host)<-[:IS_A]-(:Node)-[:HAS_ASSIGNED]->(ip) "
            
            # Get domains that resolves to given IP address
            "OPTIONAL MATCH (ip:IP)-[:RESOLVES_TO]->(domain:DomainName) "

            # Get number of security events that happened on given host
            "CALL { "  
            "   WITH ip "
            "   OPTIONAL MATCH (ip:IP)-[:SOURCE_OF]->(event:SecurityEvent) "
            "   RETURN count(event) AS event_count "
            "} "

            # Get number of cve in software running on host
            "CALL { "
            "    WITH host "
            "    MATCH (sw:SoftwareVersion)-[:ON]->(host) "
            "    WITH DISTINCT sw "
            "    MATCH (vulner:Vulnerability)-[:IN]->(sw:SoftwareVersion) "
            "    RETURN count(DISTINCT vulner) AS vulner_count "
            "} "
            
            # Get operation system running on host
            "CALL { "
            "    WITH ip, host, domain "
            "    MATCH (sw:SoftwareVersion)-[:ON]->(host) "
            "    WHERE sw.tag = \"os_component\" "
            "    WITH sw, ip "
            "    ORDER BY datetime(sw.end) DESC "
            "    LIMIT 1 "
            "    RETURN sw.version AS os "
            "} "

            # Return domains reduced to one list and rest of the variables
            "RETURN REDUCE(s = [], domain_name IN COLLECT(domain.domain_name) "
            "| s + domain_name) AS domains, "
            "ip.address AS ip, os, event_count, "
            "vulner_count, distance, path_type"
        )
        result = tx.run(query, ip=ip, max_distance=max_distance)
        return [row for row in result]
