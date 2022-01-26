from neo4j import GraphDatabase
from Model.host import Host, HostWithScore
from Model.network_service import NetworkService
from Model.software_component import SoftwareComponent
from ipaddress import ip_address
from Model.path_type import PathType
from neo4j.exceptions import ServiceUnavailable


class DatabaseConnection:
    def __init__(self, url, user, password, logger):
        self.driver = GraphDatabase.driver(url, auth=(user, password))
        self.__logger = logger

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
        :param domain: Domain name as a string
        :return: Host object
        """

        with self.driver.session() as session:
            result = session.read_transaction(self._get_ip_query, domain)

            # Domain doesn't exist in database
            if not result:
                self.__logger.critical("Given domain doesn't resolve to any IP")
                raise ValueError("Given domain doesn't resolve to any IP")

            # Create new IP address object
            ip = ip_address(result[0]["address"])

        return self.get_host_by_ip(ip)

    def get_host_by_ip(self, ip):
        """
        Finds host in the database by its IP address and initialize its
        properties. Throws ValueError when given IP doesn't exist in database.
        :param ip: IP address object
        :return: Host object
        """

        # Convert IP to string representation
        ip_str = str(ip)

        with self.driver.session() as session:
            result = session.read_transaction(self._get_host_by_ip_query,
                                              ip_str)

            # IP doesn't exist in database
            if not result:
                self.__logger.critical("Given IP was not found in database.")
                raise ValueError("Given IP was not found in database")

            # Create new host
            new_host = Host(ip,
                            result[0]["domains"],
                            result[0]["os"],
                            result[0]["antivirus"],
                            result[0]["cms"],
                            result[0]["vulner_count"],
                            result[0]["event_count"])

            # Initialize software components and network services lists
            new_host.network_services = self._get_network_services(ip_str,
                                                                   session)

        return new_host

    def get_host_with_score_by_ip(self, ip, distance, path_type, session):
        """

        :param ip:
        :param distance:
        :param path_type:
        :param session:
        :return:
        """
        # Get IP as string
        ip_str = str(ip)
        result = session.read_transaction(self._get_host_by_ip_query,
                                          ip_str)

        if not result:
            self.__logger.info(f"Given IP ({ip_str}) "
                             f"is not assigned to any host.")
            return None

        # Create new host
        new_host = HostWithScore(ip,
                                 result[0]["domains"],
                                 result[0]["os"],
                                 result[0]["antivirus"],
                                 result[0]["cms"],
                                 result[0]["vulner_count"],
                                 result[0]["event_count"],
                                 distance,
                                 path_type)

        new_host.network_services = self._get_network_services(ip_str,
                                                               session)

        return new_host

    def find_close_hosts(self, ip, max_distance):
        """
        Starts BFS traversal (uses Java traversal API) from given IP node and
        finds neighbour hosts to maximum distance given as an argument. Type
        of a path is stored as an enum.
        :param ip:
        :param max_distance:
        :return:
        """
        with self.driver.session() as session:
            result = session.read_transaction(self._find_close_hosts_query,
                                              str(ip), max_distance)

            # Initialization of a result list of hosts
            result_list = []

            # Dictionary for converting string to enum
            path_types = {"subnet": PathType.Subnet,
                          "organization": PathType.Organization,
                          "contact": PathType.Contact}

            for row in result:
                try:
                    ip = ip_address(row["ip"])
                except ValueError:
                    self.__logger.error(f"Found invalid IP address {row['ip']}")
                    continue

                new_host = self.get_host_with_score_by_ip(str(ip),
                                                          row["distance"],
                                                          path_types[row["path_type"]],
                                                          session)

                if new_host is not None:
                    result_list.append(new_host)

            return result_list

    def get_total_cve_count(self):
        """
        Counts total number of CVE that were identified in software running
        on devices in network
        :return: Total number of CVE
        """

        with self.driver.session() as session:
            result = session.read_transaction(self._get_total_cve_count_query)

        return result[0]["cve_count"]

    def get_total_event_count(self):
        """
        Counts total number of security events that happened in network
        :return: Total number of security events
        """

        with self.driver.session() as session:
            result = session.read_transaction(
                self._get_total_event_count_query)

        return result[0]["event_count"]

    def _get_network_services(self, ip, session):
        """
        Finds network services in database which runs on a host with given IP.
        :param ip: Host's IP address
        :return: List of network_service objects
        """

        result = session.read_transaction(self._get_network_services_query,
                                          str(ip))

        services = []
        for row in result:
            service = NetworkService(row["port"],
                                     row["protocol"],
                                     row["service"])
            services.append(service)
        return services

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
            "MATCH (host:Host)<-[:IS_A]-(:Node)-[:HAS_ASSIGNED]->(ip:IP) "
            "WHERE ip.address = $ip "

            # Get number of security events
            f"{DatabaseConnection.__get_host_event_count_subquery()}"

            # Get number of cve in software running on host
            f"{DatabaseConnection.__get_host_cve_count_subquery()}"

            # Get operation system running on host + optional antivirus
            f"{DatabaseConnection.__get_host_os_and_antivirus_subquery()}"
            
            # Get CMS software
            f"{DatabaseConnection.__get_cms_subquery()}"
            
            # Get domains that resolves to given IP address
            "OPTIONAL MATCH (ip:IP)-[:RESOLVES_TO]->(domain:DomainName) "

            # Return domains reduced to one list and rest of the variables
            "RETURN REDUCE(s = [], domain_name IN COLLECT(domain.domain_name) "
            "| s + domain_name) AS domains, os, antivirus, cms, event_count, "
            "vulner_count"
        )

        result = tx.run(query, ip=ip)
        return [row for row in result]

    @staticmethod
    def _get_total_event_count_query(tx):
        query = (
            "MATCH (e:SecurityEvent) "
            "RETURN count(e) AS event_count"
        )

        result = tx.run(query)
        return [row for row in result]

    @staticmethod
    def __get_host_event_count_subquery():
        return (
            "CALL { "
            "   WITH ip "
            "   OPTIONAL MATCH (ip:IP)-[:SOURCE_OF]->(event:SecurityEvent) "
            "   RETURN count(event) AS event_count "
            "} "
        )

    @staticmethod
    def _get_total_cve_count_query(tx):
        query = (
            "MATCH (v:Vulnerability) "
            "RETURN count(DISTINCT v) AS cve_count"
        )

        result = tx.run(query)
        return [row for row in result]

    @staticmethod
    def __get_host_cve_count_subquery():
        return (
            "CALL { "
            "    WITH host "
            "    MATCH (sw:SoftwareVersion)-[:ON]->(host) "
            "    WITH DISTINCT sw "
            "    MATCH (vulner:Vulnerability)-[:IN]->(sw:SoftwareVersion) "
            "    RETURN count(DISTINCT vulner) AS vulner_count "
            "} "
        )

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
    def __get_cms_subquery():
        return (
            "CALL { "
            "   WITH host "
            "   OPTIONAL MATCH (sw:SoftwareVersion)-[r:ON]->(host) "
            "   WHERE sw.tag = 'cms_client' "
            "   RETURN sw.version AS cms "
            "   LIMIT 1 "
            "} "
        )

    @staticmethod
    def _find_close_hosts_query(tx, ip, max_distance):
        query = (
            # Traverse from given IP address node
            "CALL traverse.findCloseHosts($ip, $max_distance) "
            "YIELD ip, distance, path_type "
            "RETURN ip.address AS ip, distance, path_type"
        )
        result = tx.run(query, ip=ip, max_distance=max_distance)
        return [row for row in result]

    @staticmethod
    def __get_host_os_and_antivirus_subquery():
        return (
            "CALL { "
            "   WITH host "
            "   OPTIONAL MATCH (sw:SoftwareVersion)-[r:ON]->(host) "
            # Get last OS running on host.
            "   WHERE sw.tag = 'os_component' "
            "   WITH sw, r, host "
            "   ORDER BY r.end DESC "
            "   LIMIT 1 "
            "   OPTIONAL MATCH (sw2:SoftwareVersion)-[r2:ON]->(host) "
            "   WHERE sw2.tag = 'services_component' "
            # Assure that antivirus runs on the same computer (host might be 
            # a DHCP client).
            # negation of not overlapping condition
            # => time intervals are overlapping
            "   AND NOT (r.end < r2.start OR r.start > r2.end) "
            "   RETURN sw.version AS os, sw2.version AS antivirus "
            "} "
        )
