from neo4jclient.AbsClient import AbstractClient


class RTIRClient(AbstractClient):
    def __init__(self, password, **kwargs):
        super().__init__(password=password, **kwargs)

    def create_rtir_part(self, path):
        """
        Create nodes and relationships for  rtir_component.
        1. Parse csv given in path.
        2. Create node of type [:DetectionSystem, :IP, :SecurityEvent] if not already exist.
        3. Set parameters [type, description, detection_time] of :SecurityEvent.
        4. Create relationship of type [:RAISES, :SOURCE_OF] if not already exists.

        :param path: Path to json.
        :return: neo4j object with stats about query.
        """
        path = f'file:///{path}'

        query = "CALL apoc.load.json($path) " \
                "YIELD value " \
                "UNWIND value.rtir AS entry " \
                "WITH entry.creator AS detectionsystem, entry.subject AS description, " \
                "entry.created AS detectiontime, entry.id AS id, entry.category AS type, entry.ip AS ip " \
                "MERGE(system:DetectionSystem {name: detectionsystem}) " \
                "MERGE(n:IP {address:ip}) " \
                "MERGE(sec:SecurityEvent {id:id, type:type, " \
                "description:description, detection_time:datetime(detectiontime)})  " \
                "MERGE(system)-[x:RAISES]->(sec) " \
                "MERGE(n)-[z:SOURCE_OF]->(sec) " \
                "RETURN COUNT(*)"

        params = {'path': path}

        self._run_query(query, **params)
