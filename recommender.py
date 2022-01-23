#!/usr/bin/env python
from db_connection import DatabaseConnection
from input import Input
import time
from similarity_calculator import SimilarityCalculator
from RecommenderOutput.stdout import OutputPrinter
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

    def __sort_host_list_by_risk(self):
        """
        Sorts list of host by risk of exploiting.
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

            sim_calc = SimilarityCalculator(self.db_connection,
                                            self.config,
                                            self.attacked_host)

            sim_calc.calculate_risk_scores(self.host_list)

            self.__sort_host_list_by_risk()

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
