"""Antivirus detection module

This module contains implementation of techniques for detection of antivirus
software on devices using data from network flows.
"""
import ipaddress

from services_component.rules import Rules

class Antivirus:
    """Antivirus detection class

    This class provides interface to methods intended for detection of
    antivirus software from network flow data.
    """

    def __init__(self, rules_path, target_network, logger):
        self.logger = logger
        self.rules = Rules.from_file(rules_path)
        self.target_network = target_network
        self.logger.info("Initialize")

    def run(self, flows):
        """Run antivirus detection methods on given flows

        Performs individual methods separately and then combines their results.
        :param flows: flows to process
        :return: list of objects describing detected antivirus
        """
        self.logger.info("Start")

        self.logger.info("Start", method="rule")
        rule_method = self.run_rules(flows)
        self.logger.info("Finish", method="rule", count=rule_method.count())

        final = rule_method.finalize("antivirus")
        self.logger.info("Finish", count=len(final))
        return final

    def run_rules(self, flows):
        """Attempt to match flows with the rules
        :param flows: flows to process
        :return: dictionary between IPs and predicted AVs
        """
        matches = self.rules.match(flows)
        keys = list(matches.items.keys())
        for key in keys:
            ip = ipaddress.ip_address(key)
            if not any(map(lambda x: ip in ipaddress.ip_network(x), self.target_network)):
                del matches.items[key]
        return matches
