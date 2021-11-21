#!/usr/bin/env python
from db_connection import DatabaseConnection
from input import Input
import time
from similarity_calculator import SimilarityCalculator
from Comparators import *
from output_printer import OutputPrinter
import logging


class Recommender:
    def __init__(self, bolt_url, user, password):
        self.logger = self.__initialize_logger()
        self.db_connection = DatabaseConnection(bolt_url,
                                                user, password, self.logger)
        self.comparator_list = []
        self.config = None
        self.attacked_host = None
        self.host_list = []

    def __initialize_comparators(self):
        """
        Initializes comparators used for comparing hosts.
        :return: None
        """
        self.comparator_list = [
            CveComparator(self.config["cve_cumulative"],
                          self.db_connection.get_total_cve_count()),
            EventComparator(self.config["event_cumulative"],
                            self.db_connection.get_total_event_count()),
            OsComparator(self.config["os"]),
            AntivirusComparator(self.config["antivirus"]),
            NetServicesComparator(self.config["net_service"])
            # CmsComparator
        ]

    def __sort_list_by_risk(self):
        """
        Sorts list of host by risk of exploiting.
        :return: None
        """
        self.host_list.sort(key=lambda h: h.risk, reverse=True)

    @staticmethod
    def __initialize_logger():
        """
        Initialize logging for recommender. Two loggers are used, to stderr
        output and in file "recommender.log".
        :return: Initialized logger
        """
        logger = logging.getLogger(__name__)
        logger.setLevel(20)
        # File log handler
        file_handler = logging.FileHandler("recommender.log")
        file_handler.setFormatter(
            logging.Formatter("[%(levelname)s] - %(asctime)s - %(name)s - : %(message)s"))
        file_handler.setLevel(logging.INFO)

        # stderr log handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(logging.Formatter("[%(levelname)s]: %(message)s"))
        file_handler.setLevel(logging.INFO)

        logger.addHandler(stream_handler)
        logger.addHandler(file_handler)
        return logger

    def main(self):
        input_parser = Input(self.logger)

        if input_parser.parse_options():
            if input_parser.ip is not None:
                self.attacked_host = \
                    self.db_connection.get_host_by_ip(input_parser.ip)
            else:
                self.attacked_host = \
                    self.db_connection.get_host_by_domain(input_parser.domain)

            printer = OutputPrinter(input_parser.limit, True)

            printer.print_attacked_host(self.attacked_host)
            print()

            self.config = input_parser.load_config()

            self.host_list = \
                self.db_connection.find_close_hosts(self.attacked_host.ip,
                                                    self.config["max_distance"])

            printer.print_number_of_hosts(len(self.host_list),
                                          self.config["max_distance"])

            self.__initialize_comparators()

            sim_calc = SimilarityCalculator(self.config["path"],
                                            self.attacked_host,
                                            self.comparator_list)

            sim_calc.calculate_risk_scores(self.host_list)

            self.__sort_list_by_risk()

            printer.print_host_list(self.host_list)

        self.db_connection.close()


if __name__ == "__main__":
    start_time = time.time()
    url = "bolt://localhost:7687"
    usr = "neo4j"
    user_pass = open("pass", mode='r').read()
    recommender = Recommender(url, usr, user_pass)
    recommender.main()
    print("--- %s seconds ---" % (time.time() - start_time))
