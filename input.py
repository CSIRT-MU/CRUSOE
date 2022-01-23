from sys import argv
from getopt import getopt, GetoptError
from ipaddress import ip_address
from re import match
from json import load


class Input:
    def __init__(self, logger):
        self.ip = None
        self.domain = None
        self.limit = None
        self.config_path = None
        self.__logger = logger

    def parse_options(self):
        """
        Parses input from options. Sets ip or domain attribute of attacked
        host. Optional parameters are limit - number of hosts with highest
        risk to print and config path (if no config path is given, default
        config is used.
        :return: True if options were obtained correctly, False otherwise
        """

        result = False

        try:
            # -i | --ip     -> IP input
            # -d | --domain -> domain input
            # -p | --path   –> config path
            # -l | --limit  –> number of hosts to print on output
            opts, _ = getopt(argv[1:], "i:d:c:l:", ["ip=", "domain=",
                                                    "config=", "limit="])

        except GetoptError:
            # Unsupported options
            self.__logger.critical("Invalid option(s)")
            return result

        if not opts:
            # No options were obtained
            self.__logger.critical("No arguments were given")
            return result

        for opt, arg in opts:
            if opt in ("-i", "--ip"):
                if not self.__parse_ip_address(arg):
                    return False
                result = True
            elif opt in ("-d", "--domain"):
                if not self.__parse_domain(arg):
                    return False
                result = True
            elif opt in ("-c", "--config"):
                self.config_path = arg
            elif opt in ("-l", "--limit"):
                if not self.__parse_limit(arg):
                    return False
        return result

    def load_config(self):
        """
        Loads config from path in config_path. If None, default config is used.
        :return: Config dictionary
        """
        if self.config_path is None:
            path = "default_config.json"
        else:
            path = self.config_path

        with open(path, 'r') as config_stream:
            return load(config_stream)

    def __parse_ip_address(self, address):
        """
        Checks if given string is a valid IP address, sets "ip" member if yes.
        :param address: IP address in a form of a string
        :return: True if IP was parsed correctly, False otherwise
        """
        try:
            ip = ip_address(address)
        except ValueError:
            self.__logger\
                .critical(f"Given input '{address}' is not a valid IP address")
            return False
        self.ip = ip
        return True

    def __parse_domain(self, domain):
        """
        Checks if given string is a domain name, sets "domain" member if yes.
        :param domain: Domain name to be checked
        :return: Bool (True - correct domain, False - otherwise)
        """
        if match(r"^((?=[a-z0-9-]{1,63}\.)(xn--)?[a-z0-9]+(-[a-z0-9]+)*\.)+["
                 "a-z]{2,63}.?$", domain) is None:
            return False
        self.domain = domain
        return True

    def __parse_limit(self, limit):
        """
        Checks if given limit is a correct positive integer number and sets
        limit property if yes.
        :param limit: Limit of found hosts to print on output
        :return: True if correct limit was given, false otherwise
        """
        try:
            limit_number = int(limit)
        except ValueError:
            self.__logger.critical("Limit option must be an integer value")
            return False

        if limit_number <= 0:
            self.__logger.critical("Limit must be a positive number.")
            return False

        self.limit = limit_number
        return True
