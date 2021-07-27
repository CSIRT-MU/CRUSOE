"""OS identification method using netflows -- Specific Domains

This module contains implementation of Domain class which is a method for OS
identification using Specific Domains technique. The method requires a single
setup file -- ini config which contains OS sections and corresponding domain
regular expressions.
"""

import re
import configparser
import structlog

class Domain:
    """Domain OS identification technique

    This class provides an interface for performing OS identification based on
    netflow data.
    """

    @staticmethod
    def load_reg(config_path, section):
        """Loads a section of regexes from config, compiles and returns them
        :param section: name of the section
        :return: list of compiled regexes
        """
        conf = configparser.ConfigParser()
        conf.read(config_path)
        return list(map(re.compile, conf[section].values()))

    @staticmethod
    def any_match(record, patterns):
        """Check record for match with any of the patterns
        :param record: record string to search for patterns
        :param patterns: list of regexes
        :return: True of record matched with any of the patterns; False
        otherwise
        """
        return any(map(lambda x: x.search(record), patterns))

    def __init__(self, config_path, logger=structlog.get_logger()):
        self.mapping = {
            "Windows": self.load_reg(config_path, "windows"),
            "Mac": self.load_reg(config_path, "mac"),
            "Linux": self.load_reg(config_path, "linux"),
            "Android": self.load_reg(config_path, "android"),
            "BlackBerry": self.load_reg(config_path, "blackberry"),
            "Fedora": self.load_reg(config_path, "fedora")
        }
        self.logger = logger.bind(method="domain")

    def run(self, flows):
        """Run the method on given flows
        :param flows: flows to process
        :return: dictionary between IPs and predicted operating systems
        """
        self.logger.info("Method start")

        result = {}
        for flow in flows:
            try:
                if "sa" not in flow:
                    continue
                sa = flow["sa"]
                host = flow['hhost']
                dns = flow['dnsqname']
                url = flow['hurl']

                tmp = result.get(sa, {})

                record = host + dns + url
                for os_name, patterns in self.mapping.items():
                    if self.any_match(record, patterns):
                        tmp[os_name] = tmp.get(os_name, 0) + 1

                if tmp:
                    result[sa] = tmp
            except KeyError as e:
                self.logger.warning('Flow is missing a necessary key!', key=str(e))
            except Exception as e:
                self.logger.warning(f'Exception while processing flow!', exception=str(e), flow=str(flow))

        for sa in result:
            total = sum(result[sa].values())
            for os_name in result[sa].keys():
                result[sa][os_name] /= total

        self.logger.info("Method finish")
        return result
