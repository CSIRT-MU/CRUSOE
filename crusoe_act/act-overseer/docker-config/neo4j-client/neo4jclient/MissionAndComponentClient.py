"""Neo4j client for missions and components"""

from neo4jclient.AbsClient import AbstractClient


class MissionAndComponentClient(AbstractClient):
    def __init__(self, password, **kwargs):
        super().__init__(password=password, **kwargs)

    def create_missions_and_components(self, path):
        """
        Cypher for creating missions, components, additional required nodes and relationships.

        :param path: name of json file
        :return: None
        """

        path = f'file:///{path}'

        query = "CALL apoc.load.json($path) " \
                "YIELD value " \
                "UNWIND value.nodes as nodes " \
                "UNWIND nodes.missions as missions " \
                "MERGE (mission:Mission {criticality: missions.criticality, " \
                "name: missions.name, description: missions.description, structure: apoc.convert.toJson(value)}) " \
                "WITH nodes, value " \
                "UNWIND nodes.services as components " \
                "MERGE (component:Component {name: components.name}) " \
                "WITH nodes, value " \
                "UNWIND nodes.hosts as host " \
                "MERGE (ip:IP {address: host.ip}) " \
                "MERGE (ip)<-[:HAS_ASSIGNED]-(nod:Node) " \
                "MERGE (nod)-[:IS_A]->(hos:Host {hostname: host.hostname}) " \
                "WITH value " \
                "UNWIND value.relationships as relationships " \
                "WITH relationships " \
                "UNWIND relationships.supports as supports " \
                "MATCH (mission:Mission {name: supports.from}) " \
                "MATCH (component:Component {name: supports.to}) " \
                "MERGE(mission)<-[:SUPPORTS]-(component) " \
                "WITH relationships " \
                "UNWIND relationships.has_identity as identity " \
                "MATCH (component:Component {name: identity.from}) " \
                "MATCH (host:Host {hostname: identity.to}) " \
                "MERGE(component)-[:PROVIDED_BY]->(host)"

        params = {'path': path}

        self._run_query(query, **params)

    def load_json_from_property(self, mission_name):
        """
        Load JSON from property of given mission.

        :param mission_name: name of the mission
        :return: JSON
        """

        query = "MATCH(n:Mission {name: $mission_name}) " \
                "WITH n " \
                "WITH apoc.convert.fromJsonMap(n.structure) as json_structure " \
                "RETURN json_structure"

        params = {'mission_name': mission_name}

        return self._run_query(query, **params)
