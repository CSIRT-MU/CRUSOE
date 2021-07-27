"""
Module attack_graph_test.py tests analytical process.
WARNING: These tests delete all data from the database.
"""

import unittest
import json
import pkg_resources
from neo4jclient.RESTClient import RESTClient
from crusoe_decide.test.neo4j_test_client import TestClient
from crusoe_decide.process import analytical_process

# There are exploitability scores used for vulnerabilities
# exploitability_score = {'CVE-2018-3259': 3.9,
#                         'CVE-2018-3004': 1.6,
#                         'CVE-2018-2939': 2.0,
#                         'CVE-2018-8420': 2.8,
#                         'CVE-2016-7249': 2.8,
#                         'CVE-2070-0001': 4.57,
#                         'CVE-2070-0002': 6.47,
#                         'CVE-2070-0003': 5.32,
#                         'CVE-2070-0004': 4.168,
#                         'CVE-2070-0005': 1.499}

# Set your password to Neo4j database
PASSWORD = "ne04jcrus03"

CONSTRAINT_FILE = pkg_resources.resource_filename(__name__, 'test_data/constraint.json')


class AttackGraphTestCase(unittest.TestCase):
    """
    Class for testing functionality of crusoe decide.
    """

    def test_real_world(self):
        """
        Check correctness of analytical process for real-world vulnerabilities.

        :return: None
        """
        client = TestClient(password=PASSWORD)
        client.delete_all()
        self.create_data()
        self.create_real_vulnerabilities()
        self.assertEqual({'Web mission': {'configuration': {20, 22},
                                          'probability': (0.2179, 0.2179, 0.2179)}},
                         analytical_process(neo4j_pas=PASSWORD))

        configurations = client.get_mission_configurations("Web mission")
        for conf in configurations:
            conf['configuration'].pop('time')
        self.assertCountEqual([{'configuration': {'integrity': 0.2179, 'availability': 0.2179,
                                                  'config_id': 2, 'confidentiality': 0.2179}},
                               {'configuration': {'integrity': 0.64, 'availability': 0.64,
                                                  'config_id': 1, 'confidentiality': 0.6933}}],
                              configurations)

        self.assertCountEqual([{'host': {'avail': 0.2179, 'hostname': 'host3.domain.cz',
                                         'conf': 0.2179, 'integ': 0.2179,
                                         'ip_address': '128.228.123.47'}},
                               {'host': {'avail': 0.0, 'hostname': 'host2.domain.cz',
                                         'conf': 0.0, 'integ': 0.0,
                                         'ip_address': '128.228.250.67'}},
                               {'host': {'avail': 0.64, 'hostname': 'host1.domain.cz',
                                         'conf': 0.6933, 'integ': 0.64,
                                         'ip_address': '128.228.251.133'}}],
                              client.get_missions_hosts_evaluation())

    def test_separately_app_conf_loss(self):
        """
        Check correctness of analytical process for artificial vulnerabilities that
        cause application confidentiality loss.

        :return: None
        """
        client = TestClient(password=PASSWORD)
        client.delete_all()
        self.create_data()

        self.create_fake_vulnerabilities(['Application confidentiality loss'],
                                         ['Application confidentiality loss'],
                                         ['Application confidentiality loss'],
                                         ['Application confidentiality loss'],
                                         ['Application confidentiality loss'])

        self.assertEqual({'Web mission': {'configuration': {20, 22},
                                          'probability': (0.2668, 0.0, 0.0)}},
                         analytical_process(neo4j_pas=PASSWORD))

    def test_separately_system_integ_loss(self):
        """
        Check correctness of analytical process for artificial vulnerabilities that
        cause system confidentiality loss.

        :return: None
        """
        client = TestClient(password=PASSWORD)
        client.delete_all()
        self.create_data()

        self.create_fake_vulnerabilities(['System confidentiality loss'],
                                         ['System confidentiality loss'],
                                         ['System confidentiality loss'],
                                         ['System confidentiality loss'],
                                         ['System confidentiality loss'])

        self.assertEqual({'Web mission': {'configuration': {20, 22},
                                          'probability': (0.2668, 0.0, 0.0)}},
                         analytical_process(neo4j_pas=PASSWORD))

    def test_app_cia_loss_together(self):
        """
        Check correctness of analytical process for artificial vulnerabilities that
        cause application confidentiality, integrity and availability loss.

        :return: None
        """
        client = TestClient(password=PASSWORD)
        client.delete_all()
        self.create_data()

        self.create_fake_vulnerabilities(['Application confidentiality loss',
                                          'Application integrity loss',
                                          'Application availability loss'],
                                         ['Application confidentiality loss',
                                          'Application integrity loss',
                                          'Application availability loss'],
                                         ['Application confidentiality loss',
                                          'Application integrity loss',
                                          'Application availability loss'],
                                         ['Application confidentiality loss',
                                          'Application integrity loss',
                                          'Application availability loss'],
                                         ['Application confidentiality loss',
                                          'Application integrity loss',
                                          'Application availability loss'])

        self.assertEqual({'Web mission': {'configuration': {20, 22},
                                          'probability': (0.2668, 0.2668, 0.2668)}},
                         analytical_process(neo4j_pas=PASSWORD))

    def test_gain_priv_on_app(self):
        """
        Check correctness of analytical process for artificial vulnerabilities that
        allow attacker to gain privileges on application.

        :return: None
        """
        client = TestClient(password=PASSWORD)
        client.delete_all()
        self.create_data()

        self.create_fake_vulnerabilities(['Gain privileges on application'],
                                         ['Gain privileges on application'],
                                         ['Gain privileges on application'],
                                         ['Gain privileges on application'],
                                         ['Gain privileges on application'])

        self.assertEqual({'Web mission': {'configuration': {20, 22},
                                          'probability': (0.2668, 0.2668, 0.2668)}},
                         analytical_process(neo4j_pas=PASSWORD))

    def test_gain_user_priv(self):
        """
        Check correctness of analytical process for artificial vulnerabilities that
        allow attacker to gain user privileges on system and escalate privileges.

        :return: None
        """
        client = TestClient(password=PASSWORD)
        client.delete_all()
        self.create_data()

        self.create_fake_vulnerabilities(["Gain user privileges on system",
                                          "Privilege escalation on system"],
                                         ["Gain user privileges on system",
                                          "Privilege escalation on system"],
                                         ["Gain user privileges on system",
                                          "Privilege escalation on system"],
                                         ["Gain user privileges on system",
                                          "Privilege escalation on system"],
                                         ["Gain user privileges on system",
                                          "Privilege escalation on system"])

        self.assertEqual({'Web mission': {'configuration': {20, 22},
                                          'probability': (0.1448, 0.1448, 0.1448)}},
                         analytical_process(neo4j_pas=PASSWORD))

    def test_gain_root_priv(self):
        """
        Check correctness of analytical process for artificial vulnerabilities that
        allow attacker to execute code as root.

        :return: None
        """
        client = TestClient(password=PASSWORD)
        client.delete_all()
        self.create_data()

        self.create_fake_vulnerabilities(["Arbitrary code execution as root/administrator/system"],
                                         ["Arbitrary code execution as root/administrator/system"],
                                         ["Arbitrary code execution as root/administrator/system"],
                                         ["Arbitrary code execution as root/administrator/system"],
                                         ["Arbitrary code execution as root/administrator/system"])

        self.assertEqual({'Web mission': {'configuration': {20, 22},
                                          'probability': (0.2134, 0.2134, 0.2134)}},
                         analytical_process(neo4j_pas=PASSWORD))

    def test_ip_compromised(self):
        """
        Check correctness of analytical process for artificial vulnerabilities that
        cause application confidentiality loss. One IP address in database is compromised.

        :return: None
        """
        client = TestClient(password=PASSWORD)
        client.delete_all()
        self.create_data()

        self.create_fake_vulnerabilities(['Application confidentiality loss'],
                                         ['Application confidentiality loss'],
                                         ['Application confidentiality loss'],
                                         ['Application confidentiality loss'],
                                         ['Application confidentiality loss'])

        client.set_ip_as_compromised('128.228.250.67')
        self.assertEqual({'Web mission': {'configuration': {20, 22},
                                          'probability': (0.3308, 0.0, 0.0)}},
                         analytical_process(neo4j_pas=PASSWORD))

        configurations = client.get_mission_configurations("Web mission")
        for conf in configurations:
            conf['configuration'].pop('time')
        self.assertCountEqual([{'configuration': {'integrity': 0.0, 'availability': 0.0,
                                                  'config_id': 2, 'confidentiality': 0.3308}},
                               {'configuration': {'integrity': 0.0, 'availability': 0.0,
                                                  'config_id': 1, 'confidentiality': 0.3511}}],
                              configurations)

        self.assertCountEqual([{'host': {'avail': 0.0, 'hostname': 'host3.domain.cz',
                                         'conf': 0.0, 'integ': 0.0,
                                         'ip_address': '128.228.123.47'}},
                               {'host': {'avail': 0.0, 'hostname': 'host2.domain.cz',
                                         'conf': 0.3308, 'integ': 0.0,
                                         'ip_address': '128.228.250.67'}},
                               {'host': {'avail': 0.0, 'hostname': 'host1.domain.cz',
                                         'conf': 0.3511, 'integ': 0.0,
                                         'ip_address': '128.228.251.133'}}],
                              client.get_missions_hosts_evaluation())

    @staticmethod
    def create_fake_vulnerabilities(cve1_impact, cve2_impact, cve3_impact, cve4_impact,
                                    cve5_impact):
        """
        Create fake vulnerabilities in database with specified impacts.

        :param cve1_impact: impact of the first vulnerability
        :param cve2_impact: impact of the second vulnerability
        :param cve3_impact: impact of the third vulnerability
        :param cve4_impact: impact of the fourth vulnerability
        :param cve5_impact: impact of the fifth vulnerability
        :return: None
        """
        client = TestClient(password=PASSWORD)

        client.add_vulnerability_to_resource_version(
            "oracle:database_server:12.1.0.2",
            'Assumed vulnerability with CVE ID: CVE-2070-0001'
        )
        client.create_cve_from_nvd(
            'CVE-2070-0001',
            "This CVE contains fake data and inconsistent",
            access_vector="NETWORK",
            access_complexity="LOW",
            authentication="SINGLE",
            confidentiality_impact_v2="PARTIAL",
            integrity_impact_v2="PARTIAL",
            availability_impact_v2="PARTIAL",
            base_score_v2=6.5,
            obtain_all_privilege=False,
            obtain_user_privilege=False,
            obtain_other_privilege=False,
            attack_vector="NETWORK",
            attack_complexity="HIGH",
            privileges_required="LOW",
            user_interaction="NONE",
            scope="CHANGED",
            confidentiality_impact_v3="HIGH",
            integrity_impact_v3="HIGH",
            availability_impact_v3="HIGH",
            base_score_v3=8.8,
            impact=cve1_impact,
            published_date="2016-11-10T00:29Z")

        client.add_vulnerability_to_resource_version(
            "debian:debian_linux:9.0",
            'Assumed vulnerability with CVE ID: CVE-2070-0002'
        )
        client.create_cve_from_nvd(
            'CVE-2070-0002',
            "This CVE contains fake data and inconsistent",
            access_vector="NETWORK",
            access_complexity="LOW",
            authentication="SINGLE",
            confidentiality_impact_v2="PARTIAL",
            integrity_impact_v2="PARTIAL",
            availability_impact_v2="PARTIAL",
            base_score_v2=6.5,
            obtain_all_privilege=False,
            obtain_user_privilege=False,
            obtain_other_privilege=False,
            attack_vector="LOCAL",
            attack_complexity="LOW",
            privileges_required="NONE",
            user_interaction="NONE",
            scope="UNCHANGED",
            confidentiality_impact_v3="HIGH",
            integrity_impact_v3="HIGH",
            availability_impact_v3="HIGH",
            base_score_v3=8.8,
            impact=cve2_impact,
            published_date="2016-11-10T00:29Z")

        client.add_vulnerability_to_resource_version(
            "microsoft:windows_server_2016:*",
            'Assumed vulnerability with CVE ID: CVE-2070-0003'
        )
        client.create_cve_from_nvd(
            'CVE-2070-0003',
            "This CVE contains fake data and inconsistent",
            access_vector="NETWORK",
            access_complexity="LOW",
            authentication="SINGLE",
            confidentiality_impact_v2="PARTIAL",
            integrity_impact_v2="PARTIAL",
            availability_impact_v2="PARTIAL",
            base_score_v2=6.5,
            obtain_all_privilege=False,
            obtain_user_privilege=False,
            obtain_other_privilege=False,
            attack_vector="ADJACENT_NETWORK",
            attack_complexity="LOW",
            privileges_required="NONE",
            user_interaction="REQUIRED",
            scope="UNCHANGED",
            confidentiality_impact_v3="HIGH",
            integrity_impact_v3="HIGH",
            availability_impact_v3="HIGH",
            base_score_v3=8.8,
            impact=cve3_impact,
            published_date="2016-11-10T00:29Z")

        client.add_vulnerability_to_resource_version(
            "apache:http_server:2.2",
            'Assumed vulnerability with CVE ID: CVE-2070-0004'
        )
        client.create_cve_from_nvd(
            'CVE-2070-0004',
            "This CVE contains fake data and inconsistent",
            access_vector="NETWORK",
            access_complexity="LOW",
            authentication="SINGLE",
            confidentiality_impact_v2="PARTIAL",
            integrity_impact_v2="PARTIAL",
            availability_impact_v2="PARTIAL",
            base_score_v2=6.5,
            obtain_all_privilege=False,
            obtain_user_privilege=False,
            obtain_other_privilege=False,
            attack_vector="NETWORK",
            attack_complexity="HIGH",
            privileges_required="NONE",
            user_interaction="REQUIRED",
            scope="CHANGED",
            confidentiality_impact_v3="HIGH",
            integrity_impact_v3="HIGH",
            availability_impact_v3="HIGH",
            base_score_v3=8.8,
            impact=cve4_impact,
            published_date="2016-11-10T00:29Z")

        client.add_vulnerability_to_resource_version(
            'microsoft:sql_server:2016',
            'Assumed vulnerability with CVE ID: CVE-2070-0005'
        )
        client.create_cve_from_nvd(
            'CVE-2070-0005',
            "This CVE contains fake data and inconsistent properties",
            access_vector="NETWORK",
            access_complexity="LOW",
            authentication="SINGLE",
            confidentiality_impact_v2="PARTIAL",
            integrity_impact_v2="PARTIAL",
            availability_impact_v2="PARTIAL",
            base_score_v2=6.5,
            obtain_all_privilege=False,
            obtain_user_privilege=False,
            obtain_other_privilege=False,
            attack_vector="LOCAL",
            attack_complexity="LOW",
            privileges_required="HIGH",
            user_interaction="REQUIRED",
            scope="UNCHANGED",
            confidentiality_impact_v3="HIGH",
            integrity_impact_v3="HIGH",
            availability_impact_v3="HIGH",
            base_score_v3=8.8,
            impact=cve5_impact,
            published_date="2016-11-10T00:29Z")

        for cve_id in ['CVE-2070-0001', 'CVE-2070-0002', 'CVE-2070-0003', 'CVE-2070-0004',
                       'CVE-2070-0005']:
            client.create_relationship_between_cve_and_vulnerability(
                cve_id, 'Assumed vulnerability with CVE ID: ' + cve_id)

    @staticmethod
    def create_real_vulnerabilities():
        """
        Create real-world vulnerabilities in database.

        :return: None
        """
        client = TestClient(password=PASSWORD)
        client.add_vulnerability_to_resource_version(
            'oracle:database_server:12.1.0.2',
            'Assumed vulnerability with CVE ID: CVE-2018-3259')
        client.add_vulnerability_to_resource_version(
            'oracle:database_server:12.1.0.2',
            'Assumed vulnerability with CVE ID: CVE-2018-3004')
        client.add_vulnerability_to_resource_version(
            'oracle:database_server:12.1.0.2',
            'Assumed vulnerability with CVE ID: CVE-2018-2939')
        client.create_cve_from_nvd(
            'CVE-2018-3259',
            "Vulnerability in the Java VM component of Oracle Database Server. "
            "Supported versions that are affected are "
            "11.2.0.4, 12.1.0.2, 12.2.0.1 and 18c. Easily exploitable vulnerability "
            "allows unauthenticated attacker with "
            "network access via multiple protocols to compromise Java VM. Successful attacks "
            "of this vulnerability can "
            "result in takeover of Java VM. CVSS 3.0 Base Score 9.8 (Confidentiality, "
            "Integrity and Availability impacts). "
            "CVSS Vector: (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H).",
            "NETWORK", "LOW", "NONE", "PARTIAL", "PARTIAL", "PARTIAL", 7.5, False, False, False,
            "NETWORK", "LOW", "NONE", "NONE", "UNCHANGED", "HIGH", "HIGH", "HIGH", 9.8,
            ['Gain privileges on application'], "2018-10-17T01:31Z"
        )
        client.create_cve_from_nvd(
            'CVE-2018-3004',
            "Vulnerability in the Java VM component of Oracle Database Server. "
            "Supported versions that are affected are "
            "11.2.0.4, 12.1.0.2,12.2.0.1 and 18.2. Difficult to exploit vulnerability "
            "allows low privileged attacker "
            "having Create Session, Create Procedure privilege with network access "
            "via multiple protocols to compromise "
            "Java VM. Successful attacks of this vulnerability can result in unauthorized "
            "access to critical data_old or "
            "complete access to all Java VM accessible data_old. CVSS 3.0 Base Score 5.3 "
            "(Confidentiality impacts). "
            "CVSS Vector: (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N).",
            "NETWORK", "MEDIUM", "SINGLE", "PARTIAL", "NONE", "NONE", 3.5, False, False, False,
            "NETWORK", "HIGH", "LOW", "NONE", "UNCHANGED", "HIGH", "NONE", "NONE", 5.3,
            ['Application confidentiality loss'], "2018-07-18T13:29Z"
        )
        client.create_cve_from_nvd(
            'CVE-2018-2939',
            "Vulnerability in the Core RDBMS component of Oracle Database Server. "
            "Supported versions that are affected "
            "are 11.2.0.4, 12.1.0.2, 12.2.0.1, 18.1 and 18.2. Easily exploitable vulnerability "
            "allows low privileged "
            "attacker having Local Logon privilege with logon to the infrastructure where "
            "Core RDBMS executes to "
            "compromise Core RDBMS. While the vulnerability is in Core RDBMS, attacks may "
            "significantly impact additional "
            "products. Successful attacks of this vulnerability can result in unauthorized "
            "creation, deletion or "
            "modification access to critical data_old or all Core RDBMS accessible data_old "
            "and unauthorized ability to cause "
            "a hang or frequently repeatable crash (complete DOS) of Core RDBMS. "
            "CVSS 3.0 Base Score 8.4 (Integrity and "
            "Availability impacts). CVSS Vector: (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:H).",
            "LOCAL", "LOW", "NONE", "NONE", "PARTIAL", "PARTIAL", 3.6, False, False, False,
            "LOCAL", "LOW", "LOW", "NONE", "CHANGED", "NONE", "HIGH", "HIGH", 8.4,
            ['Application integrity loss', 'Application availability loss'],
            "2018-07-18T13:29Z"
        )

        # Microsoft Windows Server
        client.add_vulnerability_to_resource_version(
            "microsoft:windows_server_2016:*",
            'Assumed vulnerability with CVE ID: CVE-2018-8420'
        )
        client.create_cve_from_nvd(
            'CVE-2018-8420',
            "A remote code execution vulnerability exists when the Microsoft XML Core Services "
            "MSXML parser processes user "
            "input, aka \"MS XML Remote Code Execution Vulnerability.\" This affects Windows 7,"
            " Windows Server 2012 R2, "
            "Windows RT 8.1, Windows Server 2008, Windows Server 2012, Windows 8.1, "
            "Windows Server 2016, Windows Server "
            "2008 R2, Windows 10, Windows 10 Servers.",
            access_vector="NETWORK",
            access_complexity="MEDIUM",
            authentication="NONE",
            confidentiality_impact_v2="COMPLETE",
            integrity_impact_v2="COMPLETE",
            availability_impact_v2="COMPLETE",
            base_score_v2=9.3,
            obtain_all_privilege=False,
            obtain_user_privilege=False,
            obtain_other_privilege=False,
            attack_vector="NETWORK",
            attack_complexity="LOW",
            privileges_required="NONE",
            user_interaction="REQUIRED",
            scope="UNCHANGED",
            confidentiality_impact_v3="HIGH",
            integrity_impact_v3="HIGH",
            availability_impact_v3="HIGH",
            base_score_v3=8.8,
            impact=['Arbitrary code execution as root/administrator/system'],
            published_date="2018-09-13T00:29Z"
        )

        client.add_vulnerability_to_resource_version(
            'microsoft:sql_server:2016',
            'Assumed vulnerability with CVE ID: CVE-2016-7249'
        )
        client.create_cve_from_nvd(
            'CVE-2016-7249',
            "Microsoft SQL Server 2016 does not properly perform a cast of an unspecified pointer,"
            " which allows remote "
            "authenticated users to gain privileges via unknown vectors, aka \"SQL RDBMS "
            "Engine Elevation of Privilege Vulnerability.\" ",
            access_vector="NETWORK",
            access_complexity="LOW",
            authentication="SINGLE",
            confidentiality_impact_v2="PARTIAL",
            integrity_impact_v2="PARTIAL",
            availability_impact_v2="PARTIAL",
            base_score_v2=6.5,
            obtain_all_privilege=False,
            obtain_user_privilege=False,
            obtain_other_privilege=False,
            attack_vector="NETWORK",
            attack_complexity="LOW",
            privileges_required="LOW",
            user_interaction="NONE",
            scope="UNCHANGED",
            confidentiality_impact_v3="HIGH",
            integrity_impact_v3="HIGH",
            availability_impact_v3="HIGH",
            base_score_v3=8.8,
            impact=['Gain user privileges on system'],
            published_date="2016-11-10T00:29Z"
        )

        for cve_id in ['CVE-2018-3259', 'CVE-2018-3004', 'CVE-2018-2939', 'CVE-2018-8420',
                       'CVE-2016-7249']:
            client.create_relationship_between_cve_and_vulnerability(
                cve_id, 'Assumed vulnerability with CVE ID: ' + cve_id)

    @staticmethod
    def create_data():
        """
        Create testing data in database.

        :return: None
        """
        client = TestClient(password=PASSWORD)
        rest_client = RESTClient(password=PASSWORD)
        for version in ["oracle:database_server:12.1.0.2", "debian:debian_linux:9.0",
                        "microsoft:windows_server_2016:*", "apache:http_server:2.2",
                        'microsoft:sql_server:2016']:
            client.create_software_version(version)
        client.create_new_host("host1.domain.cz", "host1@contact.domain")
        client.create_new_host("host2.domain.cz", "host2@contact.domain")
        client.create_new_host("host3.domain.cz", "host3@contact.domain")

        client.create_relationship_between_software_version_and_host(
            "oracle:database_server:12.1.0.2", "host1.domain.cz", 1521, "tcp")
        client.create_relationship_between_software_version_and_host_empty(
            "microsoft:windows_server_2016:*", "host1.domain.cz")
        client.create_relationship_between_software_version_and_host_empty(
            "debian:debian_linux:9.0", "host2.domain.cz")
        client.create_relationship_between_software_version_and_host(
            "apache:http_server:2.2", "host2.domain.cz", 80, "tcp")
        client.create_relationship_between_software_version_and_host(
            'microsoft:sql_server:2016', "host3.domain.cz", 1433, "tcp")
        client.create_relationship_between_software_version_and_host_empty(
            "microsoft:windows_server_2016:*", "host3.domain.cz")

        client.add_ip_to_host("host1.domain.cz", "128.228.251.133")
        client.add_ip_to_host("host2.domain.cz", "128.228.250.67")
        client.add_ip_to_host("host3.domain.cz", "128.228.123.47")
        client.create_subnet('128.228.0.0/16', 'abuse-contact@example.domain')
        client.create_relationship_between_IP_and_subnet("128.228.251.133", '128.228.0.0/16')
        client.create_relationship_between_IP_and_subnet("128.228.250.67", '128.228.0.0/16')
        client.create_relationship_between_IP_and_subnet("128.228.123.47", '128.228.0.0/16')

        with open(CONSTRAINT_FILE, "r") as constraint_file:
            data = json.load(constraint_file)
        rest_client.create_missions_and_components_string(str(data))

        client.set_relationship_between_comp_and_host(
            "DB Server service", "host1.domain.cz", 1521, "tcp",
            'oracle:database_server:12.1.0.2')
        client.set_relationship_between_comp_and_host(
            "Webserver service", "host2.domain.cz", 80, "tcp",
            "apache:http_server:2.2")
        client.set_relationship_between_comp_and_host(
            "DB Server service", "host3.domain.cz", 1433, "tcp",
            'microsoft:sql_server:2016')
