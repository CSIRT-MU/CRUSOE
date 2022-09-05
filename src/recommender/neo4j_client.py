from neo4j import GraphDatabase
from ipaddress import ip_address

from recommender.model.host import Host, HostWithScore
from recommender.model.network_service import NetworkService
from recommender.model.path_type import PathType


class Neo4jClient:
    """
    Manages connection with Neo4j database
    """

    def __init__(self, url, user, password, logger):
        self.__driver = GraphDatabase.driver(url, auth=(user, password))
        self.__logger = logger

    def close(self):
        """
        Closes connection with the Neo4j database.
        :return: None
        """
        self.__driver.close()

    def get_host_by_domain(self, domain):
        """
        Finds host in the database by its domain address and initialize its
        properties. Throws ValueError when given domain doesn't exist in the
        database.
        :param domain: Domain name string
        :return: Host object
        """

        with self.__driver.session() as session:
            result = session.read_transaction(self.__get_ip_query, domain)

            # Domain doesn't exist in the database
            if not result:
                self.__logger.critical(
                    "Given domain doesn't resolve to any IP")
                raise ValueError("Given domain doesn't resolve to any IP")

        return self.get_host_by_ip(ip_address(result["ip"]["address"]))

    def get_host_by_ip(self, ip):
        """
        Finds host in the database by its IP address and initialize its
        properties. Throws ValueError when given IP doesn't exist in database.
        :param ip: IP address object
        :return: Host object or none if host with given IP does not exist
        """

        with self.__driver.session() as session:
            result = session.read_transaction(self.__get_host_by_ip_query,
                                              str(ip))

            # IP doesn't exist in the database
            if not result:
                msg = f"Given IP ({str(ip)}) was not found in the database."
                self.__logger.critical(msg)
                raise ValueError(msg)

            # Create new host
            new_host = Host(ip, result["domains"], result["contacts"],
                            result["os"], result["antivirus"], result["cms"],
                            result["vulner_count"], result["event_count"])

            # Get network services
            new_host.network_services = self.__get_network_services(
                ip, session, result["start"], result["end"])

        return new_host

    def __get_host_with_score(self, ip, distance, path_types, session):
        """
        Gets information about nearby host which was found during the
        traversal.
        :param ip: Host's IP address object
        :param distance: Distance to the attacked host
        :param path_types: Path type(s) found to the attacked host
        :param session: Database session
        :return: HostWithScore object or None if host with given IP does not
        exist
        """
        result = session.read_transaction(self.__get_host_by_ip_query, str(ip))

        if not result:
            self.__logger.info(
                f"Given IP ({str(ip)}) is not assigned to any host.")
            return None

        new_host = HostWithScore(ip, result["domains"], result["contacts"],
                                 result["os"], result["antivirus"],
                                 result["cms"], result["vulner_count"],
                                 result["event_count"], distance, path_types)

        new_host.network_services = self.__get_network_services(
            str(ip), session, result["start"], result["end"])

        return new_host

    def find_close_hosts(self, ip, max_distance):
        """
        Starts BFS traversal (uses Java traversal API) from given IP node and
        finds nearby hosts to the maximum distance given as an argument. Type
        of a path is stored as an enum.
        :param ip: IP address object of a host where BFS should start
        :param max_distance: Maximum distance search from initial host
        :return: List of found HostWithScore objects
        """
        with self.__driver.session() as session:
            result = session.read_transaction(self.__find_close_hosts_query,
                                              ip, max_distance)

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
                    self.__logger.error(
                        f"Found invalid IP address {row['ip']}")
                    continue

                # map string path types to enum
                host_path_types = map(lambda path: path_types[path],
                                      row["path_types"])

                new_host = self.__get_host_with_score(ip, row["distance"],
                                                      host_path_types, session)

                if new_host is not None:
                    result_list.append(new_host)

            return result_list

    def get_total_cve_count(self):
        """
        Counts total number of CVE that were identified in software running
        on devices in network
        :return: Total number of CVE
        """

        with self.__driver.session() as session:
            result = session.read_transaction(self.__get_total_cve_count_query)

        return result["cve_count"]

    def get_total_event_count(self):
        """
        Counts total number of security events that happened in network.
        :return: Total number of security events
        """

        with self.__driver.session() as session:
            result = session.read_transaction(
                self.__get_total_event_count_query)

        return result["event_count"]

    def __get_network_services(self, ip, session, start, end):
        """
        Finds network services in database which runs on a host with given IP.
        :param ip: IP address of a host
        :param session: Database session
        :param start: Start of latest OS runtime
        :param end: End of latest OS runtime
        :return: List of net services
        """

        result = session.read_transaction(self.__get_network_services_query,
                                          ip, start, end)

        services = []
        for row in result:
            service = NetworkService(row["port"],
                                     row["protocol"],
                                     row["service"])
            services.append(service)
        return services

    # CYPHER queries

    @staticmethod
    def __get_ip_query(tx, domain):
        query = (
            "MATCH (ip:IP)-[:RESOLVES_TO]->(domain:DomainName) "
            "WHERE $domain IN domain.domain_name "
            "RETURN ip"
        )
        result = tx.run(query, domain=domain)
        return result.single()

    @staticmethod
    def __get_network_services_query(tx, ip, start, end):
        query = (
            "MATCH (node:Node)-[:HAS_ASSIGNED]->(ip:IP) "
            "WHERE ip.address = $ip "
            "MATCH (node)-[:IS_A]->(host:Host) "
            "MATCH (service:NetworkService)-[r:ON]->(host) "
            "WHERE NOT (r.end < $start OR r.start > $end)"
            "RETURN service"
        )
        result = tx.run(query, ip=ip, start=start, end=end)
        return [row["service"] for row in result]

    @staticmethod
    def __find_close_hosts_query(tx, ip, max_distance):
        query = (
            # Traverse from given IP address node
            "CALL traverse.findCloseHosts($ip, $max_distance) "
            "YIELD ip, distance, path_types "
            "RETURN ip, distance, path_types"
        )
        result = tx.run(query, ip=ip, max_distance=max_distance)
        return [row for row in result]

    @staticmethod
    def __get_host_by_ip_query(tx, ip):
        query = (
            "MATCH (host:Host)<-[:IS_A]-(:Node)-[:HAS_ASSIGNED]->(ip:IP) "
            "WHERE ip.address = $ip "

            # Get operating system running on host + optional antivirus and cms
            f"{Neo4jClient.__get_os_subquery()}"
            f"{Neo4jClient.__get_antivirus_subquery()}"
            f"{Neo4jClient.__get_cms_subquery()}"

            # Get number of security events
            f"{Neo4jClient.__get_host_event_count_subquery()}"

            # Get number of cve in software running on host
            f"{Neo4jClient.__get_host_cve_count_subquery()}"

            # Get contact(s) on people responsible for given host
            f"{Neo4jClient.__get_contacts_subquery()}"

            # Get domains that resolve to given IP address
            f"{Neo4jClient.__get_domains_subquery()}"

            # Return found components + timestamp of OS for finding network 
            # services
            "RETURN domains, os, contacts, antivirus, cms, event_count, "
            "vulner_count, start, end"
        )

        result = tx.run(query, ip=ip)
        return result.single()

    @staticmethod
    def __get_total_event_count_query(tx):
        query = (
            "MATCH (e:SecurityEvent) "
            "RETURN count(e) AS event_count"
        )

        result = tx.run(query)
        return result.single()

    @staticmethod
    def __get_total_cve_count_query(tx):
        query = (
            "MATCH (v:Vulnerability) "
            "RETURN count(DISTINCT v) AS cve_count"
        )

        result = tx.run(query)
        return result.single()

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
    def __get_cms_subquery():
        return (
            "CALL { "
            "   WITH host "
            "   OPTIONAL MATCH (sw:SoftwareVersion)-[r:ON]->(host) "
            "   WHERE sw.tag = 'cms_client' "
            "   RETURN sw.version AS cms "
            "   ORDER BY id(r) DESC "
            "   LIMIT 1 "
            "} "
        )

    @staticmethod
    def __get_os_subquery():
        return (
            "CALL { "
            "   WITH host "
            "   OPTIONAL MATCH (sw:SoftwareVersion)-[r:ON]->(host) "
            # Get last OS running on host.
            "   WHERE sw.tag = 'os_component' "
            "   RETURN sw.version AS os, r.start AS start, r.end AS end"
            "   ORDER BY r.end DESC "
            "   LIMIT 1 "
            "} "
        )

    @staticmethod
    def __get_antivirus_subquery():
        return (
            "CALL { "
            "   WITH host, start, end "
            "   OPTIONAL MATCH (sw:SoftwareVersion)-[r:ON]->(host) "
            "   WHERE sw.tag = 'services_component' "
            # Assure that antivirus runs on the same computer (host might be 
            # a DHCP client).
            # negation of not overlapping condition
            # => time intervals are overlapping
            "   AND NOT (end < r.start OR start > r.end) "
            "   RETURN sw.version AS antivirus "
            "   LIMIT 1 "
            "} "
        )

    @staticmethod
    def __get_contacts_subquery():
        return (
            "CALL { "
            "    WITH ip "
            "    OPTIONAL MATCH (ip:IP)-[:PART_OF]-(:Subnet)-[:HAS]->"
            "    (c:Contact) "
            "    RETURN collect(c.name) AS contacts "
            "} "
        )

    @staticmethod
    def __get_domains_subquery():
        return (
            "CALL { "
            "   WITH ip "
            "   OPTIONAL MATCH (ip:IP)-[:RESOLVES_TO]->(domain:DomainName) "
            # Reduce all found domain names in one list
            "   RETURN REDUCE(s = [], domain_name IN "
            "   COLLECT(domain.domain_name) | s + domain_name) AS domains "
            "} "
        )
