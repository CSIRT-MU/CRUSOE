"""Rules module provides tools for rule-based processing of network flows for a
purpose of detection of services running on a device.
"""

import json
from services_component.core import Result
from services_component.utils import any_match, compile_regexes, parse_range


class Rules:
    """Class for parsing and matching rule file against flows"""

    def __init__(self, rules, hooks=None):
        def prepare_ranges(range_str):
            """
            Prepare values into expected form
            """
            return parse_range(range_str) if isinstance(range_str, str) else list(map(int, range_str))

        self.hooks = {} if hooks is None else hooks

        self.rules = rules
        for rule in self.rules.values():
            if "vendor" not in rule:
                rule["vendor"] = None

            if "product" not in rule:
                rule["product"] = None

            if "version" not in rule:
                rule["version"] = None

            if "hostname" in rule:
                rule["hostname"] = compile_regexes(rule["hostname"])

            if "srcport" in rule:
                rule["srcport"] = prepare_ranges(rule["srcport"])

            if "dstport" in rule:
                rule["dstport"] = prepare_ranges(rule["dstport"])

            if "protocol" in rule:
                rule["protocol"] = [rule["protocol"]] if isinstance(rule["protocol"], str) else rule["protocol"]

            if "bytes" in rule:
                rule["bytes"] = prepare_ranges(rule["bytes"])

            if "packets" in rule:
                rule["packets"] = prepare_ranges(rule["packets"])


    @staticmethod
    def from_file(path, hooks=None):
        """Construct Rules object using given rules file path
        :param path: path to the file
        :return: newly constructed Rules object
        """
        rules = {}
        with open(path, "r") as rules_file:
            rules = json.load(rules_file)
        return Rules(rules, hooks)

    def match(self, flows):
        """Perform the matching on given flows using the rules from the constructor
        :param flows: flows to perform matching on
        :return: dictionary between IPs and the targets assigned using the rules
        """
        result = Result()

        for flow in flows:
            if "sa" not in flow:
                continue

            for rule_name, rule in self.rules.items():
                change = 1
                target = (rule["vendor"], rule["product"], rule["version"])

                if "protocol" in rule and not self.match_protocol(flow["pr"], rule["protocol"]):
                    continue

                if "srcport" in rule and not self.match_port(flow["sp"], rule["srcport"]):
                    continue

                if "dstport" in rule and not self.match_port(flow["dp"], rule["dstport"]):
                    continue

                if "bytes" in rule and not self.match_bytes(flow["byt"], rule["bytes"]):
                    continue

                if "packets" in rule and not self.match_packets(flow["pkt"], rule["packets"]):
                    continue

                if "hostname" in rule and not self.match_hostname(flow, rule["hostname"]):
                    continue

                # match => run match hook if available
                if rule_name in self.hooks:
                    target, change = self.hooks[rule_name](flow, target)

                if change != 0:
                    result[flow["sa"]][target[0]][target[1]][target[2]].inc(change)

        return result

    @staticmethod
    def match_hostname(flow, rule_hostname):
        """Check whether any of the given hostnames matches the flow
        :param flow: flow to match against
        :param rule_hostname: list of hostnames to try to match
        :return: True if match was found; False otherwise
        """
        return any(map(lambda x: any_match(flow[x], rule_hostname), ["hhost", "dnsqname", "hurl"]))

    @staticmethod
    def match_port(flow_port, rule_port):
        """Check whether a port is within a range
        :param flow_port: port to check
        :param rule_port: allowed range
        :return: True if the flow_port is within the range; False otherwise
        """
        return int(flow_port) in rule_port

    @staticmethod
    def match_protocol(flow_protocol, rule_protocol):
        """Check whether the flow protocol matches the rule
        :param flow_protocol: protocol of the flow
        :param rule_protocol: string of protocol name; or a list of them
        :return: True if the port is within the range; False otherwise
        """
        return any(map(lambda x: x == flow_protocol, rule_protocol))

    @staticmethod
    def match_bytes(flow_bytes, rule_bytes):
        """Check whether bytes value is within a range
        :param flow_bytes: bytes to check
        :param rule_bytes: allowed range
        :return: True if the flow_bytes is within the range; False otherwise
        """
        return int(flow_bytes) in rule_bytes

    @staticmethod
    def match_packets(flow_packets, rule_packets):
        """Check whether packets value is within a range
        :param flow_packets: packets to check
        :param rule_packets: allowed range
        :return: True if the flow_packets is within the range; False otherwise
        """
        return int(flow_packets) in rule_packets
