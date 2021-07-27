"""
Module responsible for network topology mapping
"""

import datetime
import os
import structlog
import nmap
import xml.etree.ElementTree as ET
import urllib.request
from urllib.error import URLError


def get_ip():
    """
    Get source ip(my ip)
    :return: IP if request was successful, empty string otherwise
    """
    try:
        return urllib.request.urlopen('https://ident.me').read().decode('utf8')
    except URLError:
        return ""


def right_replace(string, old, new, occurrence):
    """
    Take <string> and replace <old> substring with <new> substring <occurrence>-times,
    starting from the most right one match.
    :param string: string which we are changing
    :param old: substring which will be replaced
    :param new: substring which will be replacement
    :param occurrence: how many times to replace (in case of more matches)
    :return: String with replacements
    """
    candidate = string.rsplit(old, occurrence)
    return new.join(candidate)


def fix_cpe_format(cpe):
    """
    Fix cpe format before machine processing (Remove/Add necessary formatting)
    :param cpe: string which should be fixed
    :return: cpe with correct format
    """
    if cpe.startswith("cpe:/a:") or cpe.startswith("cpe:/h:") or cpe.startswith("cpe:/o:"):
        cpe = cpe[7:]
    right_delimiter_position = cpe.rfind(':')
    version_candidate = cpe[right_delimiter_position + 1:]

    # no version at all
    if not any(char.isdigit() for char in version_candidate):
        correct_version = version_candidate + ":*"
        cpe = right_replace(cpe, version_candidate, correct_version, 1)
        return cpe

    # cases with '%', '-', '.stable', '.v' in version
    for delimiter in ['%', '-', '.stable', '.v']:
        if delimiter in version_candidate:
            left_delimiter_position = version_candidate.find(delimiter)
            correct_version = version_candidate[:left_delimiter_position]
            cpe = right_replace(cpe, version_candidate, correct_version, 1)
            version_candidate = correct_version

    # special cases
    if cpe == "\"php:php:5.4.4,\"":
        return "php:php:5.4.4"
    if cpe == "microsoft:windows_server_2008:r2:sp1":
        return "microsoft:windows_server_2008:r2"
    if cpe == "linux:linux_kernel:2.6.18_pro500":
        return "linux:linux_kernel:2.6.18"
    if cpe in ["cisco:telepresence_mcu_4505", "dell:idrac8_firmware", "axis:p5534_ptz_dome_network_camera",
               "axis:m2026", "ricoh:aficio_mp_171", "kyocera:taskalfa_4052ci", "kyocera:fs", "pelco:ide10dn",
               "synology:ds209", "dell:1130n", "xerox:workcentre_5225", "xerox:phaser_6140n", "hp:laserjet_p1606",
               "ricoh:aficio_mp_c2800", "epson:wf", "oki:data_c321", "ethernut:nut_os:*", "konicaminolta:bizhub_c224e",
               "epson:aculaser_m2000", "hp:officejet_pro_8600"]:
        return cpe + ":*"

    return cpe


def scan(targets, args="", logger=structlog.get_logger()):
    """
    Prepare data from nmap to structure which can be easily updated to neo4j
    :param targets: list of hosts or networks
    :param args: args for nmap as string
    :param logger: just logger
    :return: Parsed data
    """
    logger.info("Vertical scanner started.")
    nm = nmap.PortScanner()
    data = {}
    for target in targets:
        logger.info(f"Vertical scan of {target} started.")
        data[target] = nm.scan(target, arguments=args)
        logger.info(f"Vertical scan of {target} succeeded.")
    try:
        output = {
            "data": [],
            "time": datetime.datetime.now().replace(microsecond=0).isoformat(),
            "src_ip": get_ip()
        }

        for target in data:
            info = data[target]
            for ip in info['scan']:
                cpes = []
                hosts = {"ip": ip}
                info2 = info['scan'][ip]
                if 'tcp' in info2:
                    for port in info2['tcp']:
                        if 'cpe' in info2['tcp'][port] and info2['tcp'][port]['cpe'] is not "":
                            cpes.append(fix_cpe_format(info2['tcp'][port]['cpe']))

                if 'udp' in info2:
                    for port in info2['udp']:
                        if 'cpe' in info2['udp'][port] and info2['tcp'][port]['cpe'] is not "":
                            cpes.append(fix_cpe_format(info2['udp'][port]['cpe']))

                if cpes:
                    hosts['cpe'] = cpes
                    output["data"].append(hosts)

        return output
    except KeyError:
        logger.error(f"Key error in nmap output")
        raise


def topology_scan(targets, logger=structlog.get_logger()):
    """
    Gets IP ranges to be scanned from IP set on the basis of given index.
    :param targets: list of networks/machines to be scanned
    :param logger: just logger
    :return: informations about scans in dictionary
    """
    logger.info("Topology scanner started.")
    nm = nmap.PortScanner()

    if os.getuid() != 0:
        logger.warning("Nmap traceroute typically require root permissions")

    connections = {
        "src_ip": get_ip(),
        "data": [],
        "time": datetime.datetime.now().replace(microsecond=0).isoformat()
    }

    for target in targets:
        logger.info(f"Topology scan of {target} started.")
        data = nm.scan(target, arguments="-sn -n --traceroute")
        root = ET.ElementTree(ET.fromstring(nm.get_nmap_last_output())).getroot()

        for host in root.iter("host"):
            trace = host.find("trace")
            proto = trace.get("proto")
            connection = {
                "dst_ip": host.find("address").get("addr"),
                "proto": proto,
                "hops": []
            }

            prev_ttl = 0
            if ET.iselement(trace):  # host executing the script does not have trace element
                for route in trace:
                    ttl = int(route.get("ttl"))
                    ip = route.get("ipaddr")
                    rtt = route.get("rtt")
                    data = {"ttl": ttl,
                            "ip": ip,
                            "rtt": rtt}
                    for missing_ttl in range(prev_ttl + 1, ttl):
                        connection["hops"].append({
                            "ttl": missing_ttl,
                            "ip": "null",
                            "rtt": "null"})
                    connection["hops"].append(data)
                    prev_ttl = ttl

            connections["data"].append(connection)
        logger.info(f"Topology scan of {target} succeeded.")
    return connections


def topology_scan_neo(targets, logger=structlog.get_logger()):
    """
    Gets IP ranges to be scanned from IP set on the basis of given index.
    :param targets: list of networks/machines to be scanned
    :param logger: just logger
    :return: informations about scans in dictionary
    """
    logger.info("Topology scanner started.")
    nm = nmap.PortScanner()
    my_ip = get_ip()
    if os.getuid() != 0:
        logger.warning("Nmap traceroute typically require root permissions")
    connections = {
        "data": [],
        "time": datetime.datetime.now().replace(microsecond=0).isoformat()
    }

    for target in targets:
        logger.info(f"Topology scan of {target} started.")
        nm.scan(target, arguments="-sn -n --traceroute")
        root = ET.ElementTree(ET.fromstring(nm.get_nmap_last_output())).getroot()
        for host in root.iter("host"):
            prev_ip = my_ip
            trace = host.find("trace")
            connection = {
                "dst_ip": host.find("address").get("addr"),
                "hops": []
            }

            prev_ttl = 0
            if ET.iselement(trace):  # host executing the script does not have trace element
                for route in trace:
                    ttl = int(route.get("ttl"))
                    ip = route.get("ipaddr")
                    data = {"prev_ip": prev_ip,
                            "hops": ttl - prev_ttl,
                            "next_ip": ip}
                    connection["hops"].append(data)
                    prev_ttl = ttl
                    prev_ip = ip

            connections["data"].append(connection)
        logger.info(f"Topology scan of {target} succeeded.")
    return connections, nm.get_nmap_last_output()
