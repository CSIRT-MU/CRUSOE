import logging
import sys
from json import load, dump
from os import getenv

from recommender.neo4j_client import Neo4jClient
from recommender.recommender import Recommender


class HostComparer:
    """
    Console utility for comparing two specific hosts in the database.
    """

    @staticmethod
    def main():
        """
        Compares two hosts in the database and prints a JSON to stdout containing distance, similarity and all
        partial similarities. Requires four args - comparators config path, IP addresses and maximum distance.
        :return: None
        """
        if len(sys.argv) != 5:
            print("Script requires 4 arguments - path to config, first IP, second IP and max distance.")
            sys.exit(1)

        path = sys.argv[1]
        ip1 = sys.argv[2]
        ip2 = sys.argv[3]
        max_distance = int(sys.argv[4])

        try:
            with open(path, 'r') as config_stream:
                config = load(config_stream)

            with Neo4jClient(getenv("NEO4J_URL"), getenv("NEO4J_USER"),
                             getenv("NEO4J_PASSWORD"),
                             logging.getLogger("neo4j")) as db_client:

                recommender = Recommender(config, db_client, logging.getLogger("neo4j"))

                result = recommender.compare_hosts(ip1, ip2, max_distance)

                dump(result, fp=sys.stdout, indent=4)

        except IOError or ValueError as e:
            print(str(e))
            sys.exit(1)


if __name__ == "__main__":
    HostComparer.main()
