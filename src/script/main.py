#!/usr/bin/env python

import logging
import os
import sys
from os import getenv

from recommender.neo4j_client import Neo4jClient
from recommender.recommender import Recommender
from script.stdout import StdoutPrinter
from script.csv_output import CsvOutput
from script.input import InputParser
from script.json_output import JsonOutput


class RecommenderScript:
    """
    Main recommender script.
    """

    def __init__(self):
        self.__logger = self.__initialize_logger()
        self.__input = InputParser(self.__logger)
        self.__config = None
        self.__db_config = None
        self.__recommender = None

    @staticmethod
    def __initialize_logger():
        """
        Initialize logging for the recommender. Two loggers are used (stderr
        and in file "recommender.log").
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

    def __export_result(self, ):
        """
        Exports result list in CSV or/and JSON.
        :return: None
        """
        if self.__input.json:
            JsonOutput.json_export(self.__recommender.host_list,
                                   self.__input.json)

        if self.__input.csv:
            CsvOutput.csv_export(self.__recommender.host_list,
                                 self.__input.csv)

    def __get_input_and_config(self):
        """
        Gets options, main config and database config from input parser.
        :return: True if everything was obtained successfully, False otherwise
        """
        result = self.__input.parse_options() and self.__input.load_config()

        if result:
            self.__config = self.__input.config

        return result

    def main(self):
        """
        Main recommender script.
        :return: None
        """

        # Get options and configs
        if not self.__get_input_and_config():
            # Error occurred in options or config files
            sys.exit(1)

        if "NEO4J_URL" not in os.environ or "NEO4J_USER" not in os.environ \
                or "NEO4J_PASSWORD" not in os.environ:
            self.__logger.critical("Script requires NEO4J_URL, NEO4J_USER "
                                   "and NEO4J_PASSWORD environment variables"
                                   " to be set.")
            sys.exit(1)

        # Connect to database and create recommender object
        with Neo4jClient(getenv("NEO4J_URL"), getenv("NEO4J_USER"),
                         getenv("NEO4J_PASSWORD"), self.__logger) as db_client:

            self.__recommender = Recommender(self.__config, db_client,
                                             self.__logger)

            # Find given host and recommend similar hosts
            if self.__input.ip is not None:
                self.__recommender.get_attacked_host_by_ip(self.__input.ip)
            elif self.__input.domain is not None:
                self.__recommender.get_attacked_host_by_domain(
                    self.__input.domain)

            stdout = StdoutPrinter(self.__input.limit, self.__input.verbose)
            stdout.print_attacked_host(self.__recommender.attacked_host)

            self.__recommender.recommend_hosts()

            stdout.print_number_of_hosts(len(self.__recommender.host_list))

            # Print result to screen and export in file (if set in input)
            stdout.print_host_list(self.__recommender.host_list)
            self.__export_result()


if __name__ == "__main__":
    RecommenderScript().main()
