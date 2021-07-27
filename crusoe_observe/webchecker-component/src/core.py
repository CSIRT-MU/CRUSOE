
"""
This module is responsible for  detection of unknown domain names and
assigned IPs within local network from incoming HTTP traffic and once per day
check X509 certificates of such servers
"""

import json
import socket
import ssl
import datetime
import itertools
import ipaddress
import os
import structlog
import dns.resolver
from dns.exception import DNSException


class Webchecker:
    """
    Used for checking X509 certs and discovering unknown domains
    """
    def __init__(self, config=None, logger=structlog.get_logger()):
        self.logger = logger
        self.ignore = []

        if config is not None:
            if "ignore" in config.keys():
                self.ignore = json.loads(config["ignore"])
            else:
                self.logger.warn("Config without \"ignore\" field!")
                self.ignore = []

            if "target_network" in config.keys():
                self.target_network = json.loads(config["target_network"])
            else:
                self.logger.warn("Config without \"target_network\" field!")
                self.target_network = ["0.0.0.0/0"]
        else:
            self.logger.warn("No config supplied!")

        self.target_network = list(map(ipaddress.ip_network, self.target_network))
        self.ignore = list(map(ipaddress.ip_network, self.ignore))

    def get_ips(self, hostname, ipv6=False):
        """Get IPs corresponding to given hostname (from DNS)
        :param hostname: hostname to translate
        :param ipv6: obtain IPv6 addresses
        :return: list of corresponding IPs
        """
        try:
            answers = dns.resolver.query(hostname, 'AAAA' if ipv6 else 'A')
        except DNSException:
            self.logger.warn("Could not resolve domain name.", name=hostname)
            return []
        return list(map(lambda x: str(x).split()[-1], answers.response.answer))

    def check_cert(self, hostname, port=443):
        """Perform SSL handshake and check certificate.
        :param hostname: hostname of the server
        :param port: port to connect on
        :return: Check result message; or an empty string if everything seems OK
        """
        context = ssl.create_default_context()

        try:
            with socket.create_connection((hostname, port), timeout=2.0) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    expiration = datetime.datetime.strptime(ssock.getpeercert()['notAfter'], r"%b %d %H:%M:%S %Y %Z")
                    if expiration - datetime.datetime.utcnow() < datetime.timedelta(days=31):
                        return f"Certificate will expire on {expiration.strftime('%Y-%m-%d')}."

        except ssl.CertificateError as cert_error:
            # X509_V_ERR_CERT_HAS_EXPIRED
            if cert_error.verify_code in (10,):
                return f"Expired certificate."

            # X509_V_ERR_DEPTH_ZERO_SELF_SIGNED_CERT
            # X509_V_ERR_SELF_SIGNED_CERT_IN_CHAIN
            elif cert_error.verify_code in (18, 19):
                return "Self-signed certificate."

            # X509_V_ERR_CERT_REVOKED
            elif cert_error.verify_code in (23,):
                return "Certificate revoked."

            # X509_V_ERR_HOSTNAME_MISMATCH
            elif cert_error.verify_code in (62,):
                return "Certificate hostname mismatch."

            # X509_V_ERR_*
            return "Unspecified certificate error."
        except:
            return ""  # Could not connect.

        return ""

    def run_certs(self, hostnames):
        """Process hosts and detect invalid certificates.
        :param hostnames: iterable of pairs of ips and hostnames; or just
        iterable of hostnames, however then are no IP ranges ignored
        :return: a structure suitable for database upload containing
        description of hosts and found issues
        """
        def fmt(item):
            """
            Format output
            """
            host, error = item
            return {
                "hostname": host,
                "description": error,
                "type": "cert",
                "confirmed": "false"
            }

        def ip_filter(ip):
            """
            Check whether ip should be ignored
            """
            try:
                ip = ipaddress.ip_address(ip[0])
                return not any(map(lambda x: ip in x, self.ignore))
            except:
                return False

        if len(hostnames) > 0 and isinstance(hostnames[0], tuple): # otherwise assume it's just list of hostnames
            hostnames = list(map(lambda x: x[1], filter(ip_filter, hostnames)))

        return {
            "time": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "data": list(map(fmt, filter(lambda x: x[1] != "", map(lambda y: (y, self.check_cert(y)), hostnames))))
        }

    def run_detect(self, flow_path):
        """Detect domain names in flows
        :param flow_path: path to input flows
        :return: list of structures mapping domain names to IPs
        """
        if not os.path.exists(flow_path):
            raise FileNotFoundError(f"Flow data are missing, processing time: {datetime.now()}, "
                                    f"proccessing data: {flow_path}")

        with open(flow_path, "r") as flow_file:
            flows = json.load(flow_file)

        def fmt(item):
            """
            Format output
            """
            ip, hostnames = item
            return map(lambda x: {
                "ip": ip,
                "hostname": x
            }, hostnames)

        found = {}

        try:
            timestamp = datetime.datetime.strptime(flows[0]["te"], "%Y-%m-%d %H:%M:%S.%f")
            timestamp = (timestamp - datetime.timedelta(
                minutes=-(5 - timestamp.minute % 5),
                seconds=timestamp.second,
                microseconds=timestamp.microsecond)).astimezone().isoformat()
        except:
            timestamp = ""
            self.logger.warn("Invalid format of flow data.")

        for flow in flows:
            if any(map(lambda x: x not in flow.keys(), ["da", "hhost", "dp"])):
                self.logger.info("Data from collector are missing some field.")
                continue  # some data missing

            if flow["da"] in flow["hhost"]:
                continue  # data without host

            if flow["hhost"] == "" or "." in (flow["hhost"][0], flow["hhost"][-1]):
                continue  # invalid hostname

            # IP format check
            try:
                ip = ipaddress.ip_address(flow["da"])
            except:
                self.logger.warn("Invalid IP in flow data.", da=flow["da"])
                continue

            # IP network check
            if not any(map(lambda x: ip in x, self.target_network)):
                continue  # IP not in target network

            # DNS check
            ips = self.get_ips(flow["hhost"], ip.version == 6)
            if str(ip) not in ips:
                continue  # DNS check failed

            # Assign domain name to IP in result
            if str(ip) not in found.keys():
                found[str(ip)] = set()
            found[str(ip)].add(flow["hhost"])

        return {
            "time": timestamp,
            "data": list(itertools.chain.from_iterable(map(fmt, found.items())))
        }
