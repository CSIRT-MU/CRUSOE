#!/usr/bin/env python
from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable


class DatabaseConnection:
    def __init__(self, url, user, password):
        self.driver = GraphDatabase.driver(url, auth=(user, password))

    def close(self):
        self.driver.close()

    def find_and_resolve_domain(self, domain):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_and_resolve_domain,
                                              domain)

            if result:
                return result[0]["address"]
            return None

    @staticmethod
    def _find_and_resolve_domain(tx, domain):
        query = (
            "MATCH (ip:IP)-[:RESOLVES_TO]->(domain:DomainName) "
            f"WHERE domain.domain_name = $domain "
            "RETURN ip"
        )
        result = tx.run(query, domain=domain)
        return [row["ip"] for row in result]
