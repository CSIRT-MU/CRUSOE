#!/usr/bin/python3.6
from neo4jclient.AbsClient import AbstractClient

# dictionaries which contain values for each CVSS metric used in exploitability score
ATTACK_VECTOR = {
    "NETWORK": 0.85,
    "LOCAL": 0.55,
    "ADJACENT_NETWORK": 0.62,
    "PHYSICAL": 0.2
}

ATTACK_COMPLEXITY = {
    "LOW": 0.77,
    "HIGH": 0.44
}

PRIVILEGES_REQUIRED = {
    "NONE": 0.85,
    "LOW": 0.62,
    "HIGH": 0.27
}

PRIVILEGES_REQUIRED_SCOPE_CHANGED = {
    "NONE": 0.85,
    "LOW": 0.68,
    "HIGH": 0.5
}

USER_INTERACTION = {
    "NONE": 0.85,
    "REQUIRED": 0.62
}


class AttackGraphClient(AbstractClient):
    def __init__(self, password, **kwargs):
        super().__init__(password=password, **kwargs)

    def get_exploitability(self, cve_id):
        """
        Return exploitability score of CVE.

        :param cve_id: ID of CVE
        :return:
        """
        # 8.22 * AV * AC * PR * UI - maximal value is 3.887 - to get interval (0, 1)
        # we need coefficient 8.22 / 3.887
        cve = self._run_query("MATCH (cve:CVE {CVE_id: $cve_id}) "
                              "RETURN {attack_vector: cve.attack_vector, "
                              "attack_complexity: cve.attack_complexity, "
                              "privileges_required: cve.privileges_required, "
                              "user_interaction: cve.user_interaction, "
                              "scope:cve.scope} AS cve",
                              **{'cve_id': cve_id}).single()['cve']
        if cve['scope'] == "CHANGED":
            return 2.1147 * ATTACK_VECTOR[cve['attack_vector']] * \
                   ATTACK_COMPLEXITY[cve['attack_complexity']] * \
                   PRIVILEGES_REQUIRED_SCOPE_CHANGED[cve['privileges_required']] * \
                   USER_INTERACTION[cve['user_interaction']]
        else:
            return 2.1147 * ATTACK_VECTOR[cve['attack_vector']] * \
                   ATTACK_COMPLEXITY[cve['attack_complexity']] * \
                   PRIVILEGES_REQUIRED[cve['privileges_required']] * \
                   USER_INTERACTION[cve['user_interaction']]

    def get_attack_vector(self, cve_id):
        """
        Return attack vector of CVE.

        :param cve_id: ID of CVE
        :return:
        """
        return self._run_query("MATCH (cve:CVE {CVE_id: $cve_id}) "
                               "RETURN cve.attack_vector AS attack_vector",
                               **{'cve_id': cve_id}).single()['attack_vector']

    def get_impacts(self, cve_id):
        """
        Return impacts of the CVE.

        :param cve_id: ID of CVE
        :return:
        """
        return self._run_query("MATCH (cve:CVE {CVE_id: $cve_id}) "
                               "RETURN cve.impact AS impact",
                               **{'cve_id': cve_id}).single()['impact']

    def get_attack_complexity(self, cve_id):
        """
        Return attack complexity of the CVE.

        :param cve_id: ID of CVE
        :return:
        """
        return self._run_query(
            "MATCH (cve:CVE {CVE_id: $cve_id}) "
            "RETURN cve.attack_complexity AS attack_complexity",
            **{'cve_id': cve_id}).single()['attack_complexity']

    def get_permission_to_host(self, hostname):
        """
        Return permission which are stored in the DB for the host specified by the hostname.

        :param hostname: name of host
        :return:
        """
        return self._run_query(
            "MATCH (host:Host {hostname: $hostname})-[:HAS_IDENTITY]->(dev:Device)"
            "<-[:TO]-(role:Role) "
            "RETURN {name: role.name, permission: role.permission} AS role",
            **{'hostname': hostname})

    def get_compromised_ips(self):
        """
        Returns all IPs which have their flag set to True.

        :return:
        """
        return self._run_query("MATCH (ip:IP {compromised: True}) \
                                RETURN {address: ip.address} as ip")

    def get_cves_to_software_version(self, version):
        """
        Return CVEs which are on the resource.

        :param version: software version
        :return:
        """
        return self._run_query(
            "MATCH (ver:SoftwareVersion {version: $version})<-[:IN]"
            "-(vul:Vulnerability)-[:REFERS_TO]->(cve:CVE) "
            "RETURN {CVE_id: cve.CVE_id} as cve",
            **{'version': version}
        )

    def get_network_service_to_ip(self, ip_address, mission_name):
        """
        Returns NetworkService on which the mission requirement is imposed.

        :param ip_address: IP adress
        :param mission_name: name of mission
        :return:
        """
        return self._run_query(
            "MATCH (ip:IP {address: $ip_address})<-[:HAS_ASSIGNED]-(:Node)-[:IS_A]->(host:Host)"
            "<-[r:PROVIDED_BY]-(comp:Component)-[:SUPPORTS]->(m:Mission {name: $mission_name}) "
            "RETURN DISTINCT {port:r.port, protocol:r.protocol, software:r.sw} AS service",
            **{'ip_address': ip_address, 'mission_name': mission_name})

    def get_network_service_for_software_on_ip(self, software_version, ip_address):
        """
        Returns network service on which the specified software runs.

        :param software_version: software version
        :param ip_address: IP address
        :return:
        """
        return self._run_query(
            "MATCH (ip:IP {address: $ip_address})<-[:HAS_ASSIGNED]-(:Node)-[:IS_A]->(:Host)"
            "<-[r:ON]-(v:SoftwareVersion {version: $version}) "
            "RETURN DISTINCT {port:r.port, protocol:r.protocol, software:r.sw} AS service",
            **{'ip_address': ip_address, 'version': software_version})

    def get_subnet_to_ip(self, address):
        """
        Return subnet which has the IP as a part.

        :param address: IP address
        :return:
        """
        return self._run_query("MATCH (ip:IP {address: $address})-[:PART_OF]->(subnet:Subnet) \
                                RETURN {vlan: subnet.vlan, contact: subnet.contact, \
                                range: subnet.range} AS subnet",
                               **{'address': address})

    def get_all_mission_names(self):
        """
        Return all mission in the database.

        :return:
        """
        return self._run_query("MATCH (m:Mission) RETURN {name: m.name} AS mission")

    def get_actual_network_service_to_ip(self, ip_address):
        """
        Returns recently active network services.

        :param ip_address: IP address
        :return:
        """
        return self._run_query(
            "MATCH (n:NetworkService)-[r:ON]->(:Host)<-[:IS_A]-(:Node)-[:HAS_ASSIGNED]"
            "->(ip:IP {address: $ip_address}) WITH n,r ORDER BY r.end DESC "
            "RETURN DISTINCT {port: n.port, protocol: n.protocol} AS service LIMIT 1",
            **{'ip_address': ip_address}
        )

    def get_score_for_cve(self, cve_id):
        """
        Returns CVSSv3 base score.

        :param cve_id: CVE ID
        :return:
        """
        return self._run_query("MATCH (cve:CVE {CVE_id: $cve_id}) "
                               "RETURN cve.base_score_v3 AS base_score",
                               **{'cve_id': cve_id}).single()['base_score']

    def get_actual_resources_for_ip(self, ip_address):
        """
        Returns recently detected software resources or permanent software resources
        (without timestamp).

        :param ip_address: IP address
        :return:
        """
        return self._run_query(
            "MATCH (n:SoftwareVersion)-[r:ON]->(:Host)<-[:IS_A]-(:Node)-[:HAS_ASSIGNED]"
            "->(ip:IP {address: $ip_address}) WHERE EXISTS(r.end) "
            "WITH n,r ORDER BY r.end DESC "
            "RETURN DISTINCT {version: n.version} AS resource LIMIT 2 UNION "
            "MATCH (n:SoftwareVersion)-[r:ON]->(:Host)<-[:IS_A]-(:Node)-[:HAS_ASSIGNED]"
            "->(ip:IP {address: $ip_address}) WHERE NOT EXISTS(r.end) "
            "RETURN DISTINCT {version: n.version} AS resource",
            **{'ip_address': ip_address}
        )

    def create_configuration(self, mission_name, timestamp, config_id):
        """
        Creates configuration node with the specified timestamp and ID withing the specified
        mission's configurations.

        :param mission_name: name of the mission
        :param timestamp: timestamp when the node was created
        :param config_id: ID of configuration for the specified mission
        :return:
        """
        self._run_query("CREATE (c:Configuration {config_id: $config_id, time: $timestamp}) \
                         WITH c \
                         MATCH (m:Mission {name: $name}) CREATE (m)-[:HAS]->(c)",
                        **{'config_id': config_id, 'timestamp': timestamp, 'name': mission_name})

    def add_host_to_configuration(self, hostname, mission, config_id, confidentiality, integrity,
                                  availability):
        """
        Creates relationship :CONTAINS between configuration and host. This relationship
        contains probability values for confidentiality, integrity and availability being
        compromised.

        :param hostname: name of host which should be added to configuration
        :param mission: name of the mission
        :param config_id: ID of configuration for the specified mission
        :param confidentiality: probability value for confidentiality being compromised
        :param integrity: probability value for integrity being compromised
        :param availability: probability value for availability being compromised
        :return:
        """
        self._run_query("MATCH (:Mission {name: $name})-[:HAS]->(c:Configuration "
                        "{config_id: $config_id}), (host:Host {hostname: $hostname}) \
                         CREATE (c)-[:CONTAINS {confidentiality: $conf, integrity: $integ, \
                                                availability: $avail}]->(host)",
                        **{'name': mission, 'config_id': config_id, 'hostname': hostname,
                           'conf': confidentiality,
                           'integ': integrity, 'avail': availability})

    def set_host_configuration_properties(self, hostname, mission, config_id, confidentiality,
                                          integrity, availability):
        """
        Sets probability of compromise for confidentiality, integrity and availability
        of the specified host in the specified configuration.

        :param hostname: hostname
        :param mission: name of the mission
        :param config_id: ID of configuration in the specified mission
        :param confidentiality: probability of compromise for confidentiality
        :param integrity: probability of compromise for integrity
        :param availability: probability of compromise for availability
        :return:
        """
        self._run_query("MATCH (:Mission {name: $name})-[:HAS]->(:Configuration "
                        "{config_id: $config_id})-[r:CONTAINS]->(:Host {hostname: $hostname}) \
                         SET r.confidentiality = $conf, r.integrity = $integ, \
                         r.availability = $avail",
                        **{'name': mission, 'config_id': config_id, 'hostname': hostname,
                           'conf': confidentiality,
                           'integ': integrity, 'avail': availability})

    def set_configuration_properties(self, mission_name, config_id, confidentiality, integrity,
                                     availability, timestamp):
        """
        Sets probability values for confidentiality, integrity and availability of a configuration.

        :param mission_name: name of the mission
        :param config_id: ID of configuration for the specified mission
        :param confidentiality: probability value for confidentiality being compromised
        :param integrity: probability value for integrity being compromised
        :param availability: probability value for availability being compromised
        :param timestamp: timestamp
        :return:
        """
        self._run_query("MATCH (:Mission {name: $name})-[:HAS]->(c:Configuration "
                        "{config_id: $config_id}) \
                         SET c.confidentiality = $conf, \
                             c.integrity = $integ, c.availability = $avail, c.time = $timestamp",
                        **{'name': mission_name, 'config_id': config_id, 'conf': confidentiality,
                           'integ': integrity, 'avail': availability, 'timestamp': timestamp})

    def get_hosts_for_configuration(self, mission, config_id):
        """
        Returns all hostnames for the configuration specified by its config_id and name of mission.

        :param mission: name of mission
        :param config_id: ID of configuration in the specified mission
        :return:
        """
        return self._run_query("MATCH (m:Mission {name: $name})-[:HAS]->(c:Configuration "
                               "{config_id: $config_id})-[:CONTAINS]->(h:Host) "
                               "RETURN h.hostname",
                               **{'name': mission, 'config_id': config_id}).data()
