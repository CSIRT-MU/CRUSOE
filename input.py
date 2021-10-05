from sys import argv
from getopt import getopt, GetoptError
from ipaddress import ip_address
from re import match


class Input:
    def __init__(self):
        self.ip = None
        self.domain = None

    def parse_options(self):
        """
        Parses input from options. Sets ip or domain attribute
        appropriately.
        :return: True if options were obtained correctly, False otherwise
        """
        try:
            # -i | --ip     -> IP input
            # -d | --domain -> domain input
            opts, _ = getopt(argv[1:], "i:d:", ["ip=", "domain="])

        except GetoptError:
            # Unsupported options
            print("Error - Invalid options")
            return False

        if not opts:
            # No options were obtained
            print("Error - No arguments were given")
            return False

        for opt, arg in opts:
            if opt in ("-i", "--ip"):
                self.ip = self.check_ip_address(arg)
                return True
            elif opt in ("-d", "--domain"):
                self.domain = self.check_domain(arg)
                return True

    @staticmethod
    def check_ip_address(address):
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
    def check_domain(domain):
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
