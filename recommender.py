#!/usr/bin/env python
from db_connection import DatabaseConnection
from input import Input
import time
from similarity_calculator import SimilarityCalculator
from Comparators.cve_comparator import CveComparator
from Comparators.event_comparator import EventComparator
from Comparators.os_comparator import OsComparator


class Recommender:
    def __init__(self, bolt_url, user, password):
        self.db_connection = DatabaseConnection(bolt_url, user, password)
        self.comparator_list = None
        self.config = None

    def initialize_comparators(self):
        self.comparator_list = [
            CveComparator(self.config,
                          self.db_connection.get_total_cve_count()),
            EventComparator(self.config,
                            self.db_connection.get_total_event_count()),
            OsComparator(self.config)
        ]

    def main(self):
        input_parser = Input()

        if input_parser.parse_options():
            if input_parser.ip is not None:
                attacked_host = self.db_connection.get_host_by_ip(input_parser.ip)
            else:
                attacked_host = \
                    self.db_connection.get_host_by_domain(input_parser.domain)

            print(attacked_host)

            host_list = self.db_connection.find_close_hosts(str(attacked_host.ip), 2)

            self.config = input_parser.load_config()

            self.initialize_comparators()

            sim_calc = SimilarityCalculator(self.config,
                                            attacked_host,
                                            self.comparator_list)

            sim_calc.calculate_similarities(host_list)

            for host in host_list:
                if host.risk > 0:
                    print(host.risk)

        self.db_connection.close()


if __name__ == "__main__":
    start_time = time.time()
    url = "bolt://localhost:7687"
    usr = "neo4j"
    user_pass = open("pass", mode='r').read()
    recommender = Recommender(url, usr, user_pass)
    recommender.main()
    print("--- %s seconds ---" % (time.time() - start_time))
