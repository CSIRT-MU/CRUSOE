from neo4jclient.AbsClient import AbstractClient


class SabuConnectorClient(AbstractClient):
    def __init__(self, password, **kwargs):
        super().__init__(password=password, **kwargs)

    def driver_session_if_ref_key(self, path):
        """
        Function adds relationship to DB if there's a ref key in IDEA message.

        :param: path - Path to json file
        """
        path = f'file:///{path}'
        query = "CALL apoc.load.json($path) " \
                "YIELD value as data " \
                "UNWIND (data.results) AS r " \
                "MERGE (ip:IP {address: r.ip}) " \
                "MERGE (cve:CVE {Id: r.cve_id}) " \
                "MERGE (ip)-[:CONTAINS_VULNERABILITY]->(cve)"

        params = {'path': path}
        self._run_query(query, **params)

    def driver_session_if_not_ref_key(self, path):
        """
        Function adds relationship to DB if there's no ref key in IDEA message.

        :param: path - Path to json file
        """
        path = f'file:///{path}'
        query = "CALL apoc.load.json($path) " \
                "YIELD value as data " \
                "UNWIND (data.results) AS r " \
                "MERGE (det:DetectionSystem {name:data.detection_system})" \
                "MERGE (vulnerability:SecurityEvent {detection_time:datetime(r.detection_time), " \
                "type: r.vulnerability, " \
                "description: r.description}) " \
                "MERGE (ip:IP {address: r.ip}) " \
                "MERGE (ip)-[:SOURCE_OF]->(vulnerability) " \
                "MERGE (det)-[:RAISES]-(vulnerability)"

        params = {'path': path}
        self._run_query(query, **params)
