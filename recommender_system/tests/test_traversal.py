import logging
import random
import unittest
from os import getenv

from neo4j import GraphDatabase

from recommender.neo4j_client import Neo4jClient


def get_ip_query(tx):
    query = (
        "MATCH (ip: IP) "
        "RETURN ip.address as ip "
        f"SKIP {random.randint(0, 100)} "
        "LIMIT 1 "
    )
    return tx.run(query).single()


def close_hosts_cypher_query(tx, ip, max_distance):
    query = (
        f"MATCH path = shortestPath((ip:IP)-[:PART_OF|HAS*1..{max_distance}]-(ip2:IP)) "
        "WHERE ip.address = $ip AND ip <> ip2 "
        "RETURN nodes(path) as nodes, length(path) as distance"
    )
    result = tx.run(query, ip=ip)
    return [row for row in result]


def close_hosts_traverse_query(tx, ip, max_distance):
    query = (
        "CALL traverse.findCloseHosts($ip, $max_distance) "
        "YIELD ip, distance, path_types "
        "RETURN ip, distance, path_types"
    )
    result = tx.run(query, ip=ip, max_distance=max_distance)
    return [row for row in result]


def traverse(driver, max_distance):
    with driver.session() as session:
        result = session.read_transaction(get_ip_query)

        ip = result["ip"]

        ip_set_1 = set()
        ip_set_2 = set()

        for row in session.read_transaction(close_hosts_cypher_query, ip,
                                            max_distance):
            ip_set_1.add((row["nodes"][len(row["nodes"]) - 1]["address"],
                          row["distance"]))

        for row in session.read_transaction(close_hosts_traverse_query, ip,
                                            max_distance):
            ip_set_2.add((row["ip"], row["distance"]))

    return ip_set_1, ip_set_2


class TestTraversal(unittest.TestCase):
    driver = GraphDatabase.driver(getenv("NEO4J_URL"),
                                  auth=(getenv("NEO4J_USER"),
                                        getenv("NEO4J_PASSWORD")))

    db_client = Neo4jClient(getenv("NEO4J_URL"),
                            getenv("NEO4J_USER"),
                            getenv("NEO4J_PASSWORD"),
                            logging.getLogger("neo4j"))

    def test_traversal(self):
        set1_2, set2_2 = traverse(self.driver, 2)
        self.assertEqual(set1_2, set2_2)
        set1_4, set2_4 = traverse(self.driver, 4)
        self.assertEqual(set1_4, set2_4)
        self.driver.close()


if __name__ == '__main__':
    unittest.main()
