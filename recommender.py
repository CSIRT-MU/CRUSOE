#!/usr/bin/env python
from db_connection import DatabaseConnection
from similarity_calculator import SimilarityCalculator
from RecommenderIO import *
import logging


class Recommender:
    """
    Main recommender script
    """

    def __init__(self):
        self.__logger = self.__initialize_logger()
        self.input_parser = Input(self.__logger)
        self.db_connection = None
        self.db_config = None
        self.config = None
        self.attacked_host = None
        self.host_list = []

    def __sort_host_list_by_risk(self):
        """
        Sorts list of host by risk of exploiting (descending).
        :return: None
        """
        self.host_list.sort(key=lambda h: h.risk, reverse=True)

    @staticmethod
    def __initialize_logger():
        """
        Initialize logging for recommender. Two loggers are used (stderr and
        in file "recommender.log").
        :return: Initialized logger
        """
        logger = logging.getLogger("neo4j")
        logger.setLevel(20)
        # File log handler
        file_handler = logging.FileHandler("recommender.log")
        log_format = "[%(levelname)s] - %(asctime)s - %(name)s - : %(message)s"
        file_handler.setFormatter(logging.Formatter(log_format))
        file_handler.setLevel(logging.INFO)

        # stderr log handler
        stream_handler = logging.StreamHandler()
        stderr_format = "[%(levelname)s]: %(message)s"
        stream_handler.setFormatter(logging.Formatter(stderr_format))
        file_handler.setLevel(logging.INFO)

        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)
        return logger

    def __get_attacked_host(self, input_parser):
        """
        Loads attacked host from database in attacked_host attribute.
        :param input_parser: Recommender input parser
        :return: None
        """
        if input_parser.ip is not None:
            self.attacked_host = \
                self.db_connection.get_host_by_ip(input_parser.ip)
        elif input_parser.domain is not None:
            self.attacked_host = \
                self.db_connection.get_host_by_domain(input_parser.domain)

    def __export_result(self, ):
        """
        Exports result list in CSV or/and JSON.
        :return: None
        """
        if self.input_parser.json:
            JsonOutput.json_export(self.host_list, self.input_parser.verbose,
                                   self.input_parser.json)

        if self.input_parser.csv:
            CsvOutput.csv_export(self.host_list, self.input_parser.verbose,
                                 self.input_parser.csv)

    def __get_input_and_configs(self):
        """
        Gets options, main config and database config from input parser.
        :return: True if everything was obtained successfully, False otherwise
        """
        result = self.input_parser.parse_options() and \
            self.input_parser.load_config() and \
            self.input_parser.load_db_config()

        if result:
            self.config = self.input_parser.config
            self.db_config = self.input_parser.db_config

        return result

    def main(self):
        """
        Main recommender method.
        :return: None
        """

        # 1) Get options and configs
        if not self.__get_input_and_configs():
            # Error occurred in options or config files
            return

        # 2) Connect to database
        self.db_connection = DatabaseConnection(self.db_config, self.__logger)

        # 3) Find given host from input in the database
        self.__get_attacked_host(self.input_parser)

        printer = \
            stdout.StdoutPrinter(self.input_parser.limit,
                                 self.input_parser.verbose)

        printer.print_attacked_host(self.attacked_host)

        # 4) Start BFS from attacked host IP and find hosts in close proximity
        self.host_list = self.db_connection.find_close_hosts(
            self.attacked_host.ip,
            self.config["max_distance"])

        printer.print_number_of_hosts(len(self.host_list),
                                      self.config["max_distance"])

        # 5) Calculate risk scores
        sim_calc = SimilarityCalculator(self.db_connection,
                                        self.config,
                                        self.attacked_host)

        sim_calc.calculate_risk_scores(self.host_list)

        # 6) Sort host list by risk score descending
        self.__sort_host_list_by_risk()

        # 7) Print result to screen and export in file (if set in config)
        printer.print_host_list(self.host_list)
        self.__export_result()

        # 8) Close connection with database
        self.db_connection.close()


if __name__ == "__main__":
    recommender = Recommender()
    recommender.main()
