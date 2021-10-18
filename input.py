from sys import argv
from getopt import getopt, GetoptError
from ipaddress import ip_address
from re import match
from json import load


class Input:
    def __init__(self):
        self.ip = None
        self.domain = None
        self.config_path = None

    def parse_options(self):
        """
        Parses input from options. Sets ip or domain attribute
        appropriately.
        :return: True if options were obtained correctly, False otherwise
        """

        result = False

        try:
            # -i | --ip     -> IP input
            # -d | --domain -> domain input
            # -p | --path   –> config path
            opts, _ = getopt(argv[1:], "i:d:c:", ["ip=", "domain=", "config="])

        except GetoptError:
            # Unsupported options
            print("Error - Invalid options")
            return result

        if not opts:
            # No options were obtained
            print("Error - No arguments were given")
            return result

        for opt, arg in opts:
            if opt in ("-i", "--ip"):
                self.ip = self._check_ip_address(arg)
                result = True
            elif opt in ("-d", "--domain"):
                self.domain = self._check_domain(arg)
                result = True
            elif opt in ("-c", "--config"):
                self.config_path = arg

        return result

    def load_config(self):
        if self.config_path is None:
            path = "default_config.json"
        else:
            path = self.config_path

        with open(path, 'r') as config_stream:
            return load(config_stream)

    @staticmethod
    def _check_ip_address(address):
        """
        Checks if given string is a valid IP address
        :param address: IP address in string
        :return: IP address object or None
        """
        try:
            ip = ip_address(address)
        except ValueError:
            print(f"Given input '{address}' is not a valid IP address")
            return None
        return ip

    @staticmethod
    def _check_domain(domain):
        """
        Checks if given string is a domain name
        :param domain: Domain name
        :return:
        """
        if match(r"^((?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+(-[a-z0-9]+)*\.)+["
                 "a-z]{2,63}.?$", domain) is None:
            print(f"Given input '{domain}' is not a valid domain name")
            return None

        return domain
