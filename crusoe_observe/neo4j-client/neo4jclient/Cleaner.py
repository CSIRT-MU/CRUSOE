#!/usr/bin/python3.6
from neo4jclient.AbsClient import AbstractClient


class Cleaner(AbstractClient):
    def __init__(self, password, **kwargs):
        super().__init__(password=password, **kwargs)
        self.duration = 'P4M'
        self.duration_on_relationship = 'P42D'

    def clean_security_event(self):
        """
        Clean security events which are older than specified duration and were produced by:
         1. Shadowserver/Shodan (vulnerability component)
         2. Webchecker
         3. Sabu component
         4. RTIR component

        :return: Number of deleted nodes
        """

        query = "CALL apoc.periodic.commit('" \
                "WITH datetime() - duration($duration) AS popTime " \
                "MATCH(secEvent:SecurityEvent) " \
                "WHERE secEvent.detection_time < popTime " \
                "WITH secEvent LIMIT {limit} " \
                "DETACH DELETE secEvent " \
                "RETURN count(*)', {limit:1000, duration: {duration}})"

        params = {'duration': self.duration}

        return self._run_query(query, **params).single().value()

    def clean_old_domains(self):
        """
        Clean information about domain resolving.
        Delete :RESOLVES_TO relationship if it is older than specified duration.

        :return: Number of deleted relationships
        """
        query = "CALL apoc.periodic.commit('" \
                "WITH datetime() - duration($duration) AS popTime " \
                "MATCH(ip:IP)-[r:RESOLVES_TO]->(domain:DomainName) " \
                "WHERE r.last_detected < popTime " \
                "WITH r LIMIT {limit} " \
                "DELETE r " \
                "RETURN count(*)', {limit:1000, duration: {duration}})"

        params = {'duration': self.duration}

        return self._run_query(query, **params).single().value()

    def clean_topology(self):
        """
        Clean relationship :IS_CONNECTED_TO if it is older than specified duration.

        :return: Number of deleted relationships
        """
        query = "CALL apoc.periodic.commit('" \
                "WITH datetime() - duration($duration) AS popTime " \
                "MATCH (first:Node)-[r:IS_CONNECTED_TO]->(another:Node) " \
                "WHERE r.last_detection < popTime " \
                "WITH r LIMIT {limit} " \
                "DELETE r " \
                "RETURN count(*)',  {limit:1000, duration: {duration}})"

        params = {'duration': self.duration}

        return self._run_query(query, **params).single().value()

    def clean_network_services(self):
        """
        Clean relationship :ON if it is older than specified duration and is connected with NetworkService.

        :return: Number of deleted relationships
        """
        query = "CALL apoc.periodic.commit('" \
                "WITH datetime() - duration($duration_on_relationship) AS popTime " \
                "MATCH(service:NetworkService)-[r:ON]->(host:Host) " \
                "WHERE r.end < popTime " \
                "WITH r LIMIT {limit} " \
                "DELETE r " \
                "RETURN count(*)',  {limit:10000, duration_on_relationship: {duration_on_relationship}})"

        params = {'duration_on_relationship': self.duration_on_relationship}

        return self._run_query(query, **params).single().value()

    def clean_software_versions(self):
        """
        Clean relationship :ON if it is older than specified duration and is connected with SoftwareResource.

        :return: Number of deleted relationships
        """
        query = "CALL apoc.periodic.commit('" \
                "WITH datetime() - duration($duration_on_relationship) AS popTime " \
                "MATCH(software:SoftwareVersion)-[r:ON]->(host:Host) " \
                "WHERE r.end < popTime " \
                "WITH r LIMIT {limit} " \
                "DELETE r " \
                "RETURN count(*)',  {limit:10000, duration_on_relationship: {duration_on_relationship}})"

        params = {'duration_on_relationship': self.duration_on_relationship}

        return self._run_query(query, **params).single().value()
