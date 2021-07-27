"""
Module generator.py contains functionality which generates input file for MULVAL. This file
contains facts which are defined in MULVAL's interaction rules file.
"""

import re
import os

# This dictionary converts impact from classifier into constants suitable for MULVAL
ATTACK_DICTIONARY = {
    'Gain user privileges on system': 'gainUserPrivileges',
    'Gain privileges on application': 'gainPrivOnApp',
    'Arbitrary code execution as user of application': 'gainPrivOnApp',
    'Gain root/system/administrator privileges on system': 'gainRootPrivileges',
    'Arbitrary code execution as root/administrator/system': 'gainRootPrivileges',
    'Privilege escalation on system': 'privEscalationOnSystem',
    'Application confidentiality loss': 'appConfidentialityLoss',
    'Application integrity loss': 'appIntegrityLoss',
    'Application availability loss': 'appAvailabilityLoss',
    'System confidentiality loss': 'systemConfidentialityLoss',
    'System integrity loss': 'systemIntegrityLoss',
    'System availability loss': 'systemAvailabilityLoss'
}


def generate_input_file(mission, goal_host, hosts, path, mulval_dir, client, logger):
    """
    This function generates input file to be processed by the MULVAL according to
    the set of components and goal component - goal of an attack.

    :param mission: the mission for which the attack graph will be created
    :param goal_host: goal of an attack
    :param hosts: set of components for which the file is generated
    :param path: path where the file is written
    :param mulval_dir: directory where the input file is stored
    :param client: Neo4j client
    :param logger: logger for logging progress of algorithm and time information
    :return: None
    """
    logger.info("Generating input file.")
    if not os.path.exists(mulval_dir):
        os.mkdir(mulval_dir)
    with open(path, "w") as txtfile:
        write_compromised_hosts(client, txtfile)

        file_lines = set()

        write_attack_goals(client, txtfile, file_lines, mission, goal_host)

        for host in hosts:
            resources = client.get_actual_resources_for_ip(host['ip']).data()
            for resource in resources:
                resource_name = resource['resource']['version']
                resource_variable = re.sub(r'\W+', '_', resource_name)
                ip_variable = "ip_" + re.sub(r'\W+', '_', host['ip'])
                if resource_variable != "_":
                    write_fact_into_file(txtfile, file_lines,
                                         f"installed({ip_variable}, {resource_variable}).\n")

                write_network_service_info(client, txtfile, file_lines, host, resource_name,
                                           resource_variable)
                write_cve_properties(client, txtfile, file_lines, host, resource_name,
                                     resource_variable)
            write_subnet_info(client, txtfile, file_lines, host)
            write_open_ports_info(client, txtfile, file_lines, host)

        # this fact is always true - each machine can access itself
        txtfile.write("hacl(H,H,_,_).\n")
    logger.info("Input file created successfully.")


def write_fact_into_file(txtfile, written_lines, fact):
    """
    Writes a fact (in logical programming terminology) and tests whether it is already written.

    :param txtfile: file which is written to
    :param written_lines: lines which are already written
    :param fact: fact to be written
    :return: None
    """
    if fact not in written_lines:
        written_lines.add(fact)
        txtfile.write(fact)


def write_compromised_hosts(client, txtfile):
    """
    Writes to the file which hosts are compromised. Default position of an attacker is internet.

    :param client: neo4j client
    :param txtfile: file to be written to
    :return: None
    """
    txtfile.write("attackerLocated(internet).\n")
    compromised_ips = client.get_compromised_ips().data()
    for raw_ip in compromised_ips:
        ip = raw_ip['ip']['address']
        ip_variable = "ip_" + re.sub(r'\W+', '_', ip)
        txtfile.write(f"attackerLocated({ip_variable}).\n")


def write_attack_goals(client, txtfile, written_lines, mission, goal_host):
    """
    Writes to the file goals of an attack.

    :param client: neo4j client
    :param txtfile: file to be written to
    :param written_lines: lines which are already written to file
    :param mission: actually processed mission
    :param goal_host: goal of an attack
    :return: None
    """
    # there will be added functionality when we do not need all requirements
    service_raw = client.get_network_service_to_ip(goal_host['ip'], mission).single()
    if service_raw:
        service = service_raw['service']

    ip_variable = "ip_" + re.sub(r'\W+', '_', goal_host['ip'])
    if service_raw and 'protocol' in service and service['protocol'] is not None:
        # this requirement is imposed on the application
        resource_name = service['software']
        resource_variable = re.sub(r'\W+', '_', resource_name)
        write_fact_into_file(txtfile, written_lines, f"attackGoal(appConfLoss({ip_variable}, "
                                                     f"{resource_variable})).\n")
        write_fact_into_file(txtfile, written_lines, f"attackGoal(appIntegLoss({ip_variable}, "
                                                     f"{resource_variable})).\n")
        write_fact_into_file(txtfile, written_lines, f"attackGoal(appAvailLoss({ip_variable}, "
                                                     f"{resource_variable})).\n")
    else:
        # this requirement is imposed on the host
        write_fact_into_file(txtfile, written_lines, f"attackGoal(sysConfLoss({ip_variable})).\n")
        write_fact_into_file(txtfile, written_lines, f"attackGoal(sysIntegLoss({ip_variable})).\n")
        write_fact_into_file(txtfile, written_lines, f"attackGoal(sysAvailLoss({ip_variable})).\n")


def write_network_service_info(client, txtfile, written_lines, host, resource_name,
                               resource_variable):
    """
    This function writes information about network services.

    :param client: neo4j client
    :param txtfile: file to be written to
    :param written_lines: lines which are already written to file
    :param host: host on which the services run
    :param resource_name: name of the resource
    :param resource_variable: resource name which could be processed by MULVAL
    :return: None
    """
    service = client.get_network_service_for_software_on_ip(resource_name,
                                                            host['ip']).single()['service']

    ip_variable = "ip_" + re.sub(r'\W+', '_', host['ip'])

    if service['port'] is not None:
        raw_permission = client.get_permission_to_host(host['hostname']).single()
        if raw_permission is None:
            permission = "_"
        else:
            permission = raw_permission['role']['permission']

        write_fact_into_file(
            txtfile, written_lines,
            f"networkServiceInfo({ip_variable}, {resource_variable}, "
            f"{service['protocol']}, {str(service['port'])}, {permission}).\n")

        write_fact_into_file(
            txtfile, written_lines,
            f"hacl(internet, {ip_variable}, {service['protocol']}, "
            f"{str(service['port'])}).\n")


def write_open_ports_info(client, txtfile, written_lines, host):
    """
    This function writes information about opened ports.

    :param client: neo4j client
    :param txtfile: file to be written to
    :param written_lines: lines which are already written to file
    :param host: host on which the ports are opened
    :return: None
    """
    services = client.get_actual_network_service_to_ip(host['ip']).data()
    ip_variable = "ip_" + re.sub(r'\W+', '_', host['ip'])
    for service in services:
        write_fact_into_file(
            txtfile, written_lines,
            f"hacl(internet, {ip_variable}, {service['service']['protocol'].lower()}, "
            f"{str(service['service']['port'])}).\n")

        write_fact_into_file(
            txtfile, written_lines,
            f"networkServiceInfo({ip_variable}, _, {service['service']['protocol'].lower()}, "
            f"{str(service['service']['port'])}, _).\n")


def write_subnet_info(client, txtfile, written_lines, host):
    """
    This function writes information about subnets.

    :param client: neo4j client
    :param txtfile: file to be written to
    :param written_lines: lines which are already written to file
    :param host: host on which the services run
    :return: None
    """
    ip_address = host['ip']
    ip_variable = "ip_" + re.sub(r'\W+', '_', ip_address)
    subnets = client.get_subnet_to_ip(ip_address).data()
    for subnet in subnets:
        subnet_range = subnet['subnet']['range']
        write_fact_into_file(txtfile, written_lines,
                             f"inSubnet({ip_variable}, '{subnet_range}').\n")


def write_cve_properties(client, txtfile, written_lines, host, resource_name, resource_variable):
    """
    This function writes information about CVE existence. Since the count of CVEs which
    could appear in the Bayesian Network is restricted, we take for each impact category
    only one CVE. The algorithm prefers such CVEs which are remotely exploitable
    and have the highest score.

    :param client: neo4j client
    :param txtfile: file to be written to
    :param written_lines: lines which are already written to file
    :param host: host on which the resources run
    :param resource_name: name of the resource
    :param resource_variable: resource name which could be processed by MULVAL
    :return: None
    """

    resource_cves = client.get_cves_to_software_version(resource_name).data()
    ip_variable = "ip_" + re.sub(r'\W+', '_', host['ip'])
    used_impacts = {}

    for cve in resource_cves:
        cve_id = cve['cve']['CVE_id']
        attack_vector = client.get_attack_vector(cve_id)
        if attack_vector in ('LOCAL', 'PHYSICAL'):
            exploit = 'localExploit'
        else:
            exploit = 'remoteExploit'
        list_of_impacts = client.get_impacts(cve_id)
        for impact in list_of_impacts:
            if impact in ATTACK_DICTIONARY:
                cve_score = client.get_score_for_cve(cve_id)
                if impact in used_impacts:
                    if used_impacts[impact][1] < cve_score and \
                            (exploit == 'remoteExploit' or
                             (exploit == 'localExploit' and
                              used_impacts[impact][2] == 'localExploit')):
                        used_impacts[impact] = (cve_id, cve_score, exploit)
                else:
                    used_impacts[impact] = (cve_id, cve_score, exploit)
            else:
                raise ValueError("Unspecified impact")

    for impact in used_impacts:
        cve_id = used_impacts[impact][0]
        exploit = used_impacts[impact][2]
        write_fact_into_file(
            txtfile, written_lines,
            f"vulExists({ip_variable}, '{cve_id}', {resource_variable}).\n")
        predicate_impact = ATTACK_DICTIONARY[impact]
        write_fact_into_file(txtfile, written_lines,
                             f"vulProperty('{cve_id}', {exploit}, {predicate_impact}).\n")
        attack_complexity = client.get_attack_complexity(cve_id)
        write_fact_into_file(txtfile, written_lines, f"cvss('{cve_id}', '{attack_complexity}').\n")
