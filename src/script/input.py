from sys import argv
from getopt import getopt, GetoptError
from json import load

from utils.validator import Validator


class InputParser:
    """
    Parses all input needed for the recommender script.
    """

    def __init__(self, logger):
        self.ip = None
        self.domain = None
        self.limit = None
        self.verbose = False
        self.config = None
        self.__config_path = None
        self.csv = None
        self.json = None
        self.__logger = logger

    def parse_options(self):
        """
        Parses input from options. Sets the IP or domain attribute of the
        attacked host. Optional parameters are limit - number of hosts with
        the highest risk to print, verbose and config path (if no config path
        is given, the default config is used. The result can also be exported
        in CSV and JSON.
        :return: True if options were obtained correctly, False otherwise
        """

        result = False

        try:
            # -i | --ip      -> IP input
            # -d | --domain  -> domain input
            # -c | --config  –> config path
            # -l | --limit   –> number of hosts to print on output
            # -v | --verbose -> use verbose output
            # -s | --csv     -> export in csv
            # -j | --json    –> export in json
            opts, _ = getopt(argv[1:], "i:d:c:l:j:s:v",
                             ["ip=", "domain=", "config=", "limit=", "json=",
                              "csv=", "verbose"])

        except GetoptError:
            # Unsupported options
            self.__logger.critical("Invalid option(s)")
            return False

        if not opts:
            # No options were obtained
            self.__logger.critical("No arguments were given")
            return False

        for opt, arg in opts:
            if opt in ("-i", "--ip"):
                if not Validator.validate_ip(arg):
                    self.__logger.critical("Invalid IP address.")
                    return False
                self.ip = arg
                result = True
            elif opt in ("-d", "--domain"):
                if not Validator.validate_domain(arg):
                    self.__logger.critical("Invalid domain name.")
                    return False
                self.domain = arg
                result = True
            elif opt in ("-c", "--config"):
                self.__config_path = arg
            elif opt in ("-l", "--limit"):
                if not Validator.validate_positive_integer(arg):
                    self.__logger.critical("Invalid limit option.")
                    return False
                self.limit = int(arg)
            elif opt in ("-c", "--csv"):
                self.csv = arg
            elif opt in ("-j", "--json"):
                self.json = arg
            elif opt in ("-v", "--verbose"):
                self.verbose = True

        return result

    def load_config(self):
        """
        Loads config from the path in config_path. If None, the default config
        is used.
        :return: True if config was successfully parsed, False otherwise.
        """
        if self.__config_path is None:
            path = "default_config.json"
        else:
            path = self.__config_path

        try:
            with open(path, 'r') as config_stream:
                self.config = load(config_stream)
        except IOError:
            self.__logger.critical("Error while loading config file.")
            return False

        return True
