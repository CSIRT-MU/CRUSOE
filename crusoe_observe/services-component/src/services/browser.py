"""Browser detection module

This module contains implementation of techniques for detection of web browser
software on devices using data from network flows.
"""
from services_component.rules import Rules

class Browser:
    """Browser detection class

    This class provides interface to methods intended for detection of
    web browser software from network flow data.
    """

    def __init__(self, ua_path, domains_path, logger):
        self.logger = logger
        self.ua = Rules.from_file(ua_path)
        self.domains = Rules.from_file(domains_path)
        self.logger.info("Initialize")

    def run(self, flows):
        """Run web browser detection methods on given flows

        Performs individual methods separately and then combines their results.
        :param flows: flows to process
        :return: list of objects describing detected web browser
        """
        self.logger.info("Start")

        self.logger.info("Start", method="ua")
        ua_method = self.run_ua(flows)
        self.logger.info("Finish", method="ua", count=ua_method.count())

        self.logger.info("Start", method="domains")
        domains_method = self.run_domains(flows)
        self.logger.info("Finish", method="domains", count=domains_method.count())

        final = Result()
        final.merge(ua_method)
        final.merge(domains_method, 5.0)

        final = final.finalize("browser")
        self.logger.info("Finish", count=len(final))
        return final

    def run_ua(self, flows):
        """Attempt to match flows with User-Agent rules
        :param flows: flows to process
        :return: Result object with browsers
        """
        return self.ua.match(flows)

    def run_domains(self, flows):
        """Attempt to match flwos with Specific Domain rules
        :param flows: flows to process
        :return: Result object with browsers
        """
        return self.domains.match(flows)
