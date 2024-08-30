import logging
import sys
from json import load, dump
from os import getenv
from statistics import mean

from recommender.comparators import *
from recommender.neo4j_client import Neo4jClient


class MeanBoundCalculator:
    """
    Calculates critical bounds in configuration, based on average similarity.
    """

    @staticmethod
    def __calc_cpe_mean_bound(comparator, versions):
        """
        Calculates similarity for all software version combinations possible
        and sets critical bound as a mean of all similarities.
        :param versions: SoftwareComponent objects of all distinct software
        version found
        :return: mean similarity of all combinations
        """
        similarities = []
        for i in range(len(versions)):
            for j in range(i, len(versions)):
                similarities.append(
                    comparator.compare_sw_components(versions[i], versions[j]))

        return mean(map(lambda x: x[0], similarities))

    @staticmethod
    def calculate_mean_bounds(db_client, config):
        """
        Calculates mean bounds for cumulative similarities and similarities
        based one CPE strings. Uses computationally intensive Cypher queries
        and generates a lot of combinations, thus calculation might take
        several minutes.
        :param db_client: Neo4j client
        :param config: Recommender configuration (dictionary)
        :return:
        """
        os = OsComparator(config["comparators"]["os"])
        all_os = db_client.get_all_os_versions()
        avg_os = MeanBoundCalculator.__calc_cpe_mean_bound(os, all_os)

        config["comparators"]["os"]["critical_bound"] = round(avg_os, 8)

        cms = OsComparator(config["comparators"]["cms"])
        all_cms = db_client.get_all_cms_versions()
        avg_cms = MeanBoundCalculator.__calc_cpe_mean_bound(cms, all_cms)

        config["comparators"]["cms"]["critical_bound"] = round(avg_cms, 8)

        antivirus = OsComparator(config["comparators"]["antivirus"])
        all_antivirus = db_client.get_all_antivirus_versions()
        avg_anti = MeanBoundCalculator.__calc_cpe_mean_bound(antivirus,
                                                             all_antivirus)

        config["comparators"]["antivirus"]["critical_bound"] = round(avg_anti,
                                                                     8)

        # For cumulative similarities, mean bound is calculated as mean of
        # number of events/vulnerabilities found on hosts divided by total
        # number of them found in the network.
        avg_cve = db_client.get_average_cve_count()
        total_cve = db_client.get_total_cve_count()
        config["comparators"]["cve_cumulative"]["critical_bound"] = \
            round(avg_cve / total_cve, 8)

        avg_event = db_client.get_average_event_count()
        total_event = db_client.get_total_event_count()
        config["comparators"]["event_cumulative"]["critical_bound"] = \
            round(avg_event / total_event, 8)

    @staticmethod
    def main():
        """
        Runs calculator as a console utility.
        :return: None
        """
        if len(sys.argv) != 2:
            print("Script requires one argument - path to config.")
            sys.exit(1)

        path = sys.argv[1]

        try:
            with open(path, 'r') as config_stream:
                config_json = load(config_stream)

            with Neo4jClient(getenv("NEO4J_URL"), getenv("NEO4J_USER"),
                             getenv("NEO4J_PASSWORD"),
                             logging.getLogger("neo4j")) as db_client:
                MeanBoundCalculator.calculate_mean_bounds(db_client,
                                                          config_json)

            with open(path, 'w') as config_stream:
                dump(config_json, config_stream, indent=4)

            print("Calculated mean bounds successfully.")

        except IOError as e:
            print(str(e))
            sys.exit(1)


if __name__ == "__main__":
    MeanBoundCalculator.main()
