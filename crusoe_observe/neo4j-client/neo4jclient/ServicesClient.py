from neo4jclient.AbsClient import AbstractClient


class ServicesClient(AbstractClient):
    def __init__(self, password, **kwargs):
        super().__init__(password=password, **kwargs)

    def create_service_component(self, path, mode=None):
        """
        Create nodes and relationships for service component.
        -------------
        Antivirus_query:
        1. Parse csv given in path.
        2. Create node of type [:SoftwareVersion, :IP] if not already exists.
        3. Create node of type [:Host], relationship of type [:ON] with parameters [start,end] if not already exists.
        Otherwise just update information about time on parameters [start,end].
        4. Create node of type [:Node], relationship of type [:HAS_ASSIGNED].
        5. Create relationship of type [:IS_A] between :Host and :Node if not already exists.
        --------------
        Network_services_query:
        1. Parse csv given in path.
        2. Create node of type [:NetworkService, :IP] if not already exists.
        3. Create node of type [:Host], relationship of type [:ON] with parameters [start,end] if not already exists.
        Otherwise just update information about time on parameters [start,end].
        4. Create node of type [:Node], relationship of type [:HAS_ASSIGNED].
        5. Create relationship of type [:IS_A] between :Host and :Node if not already exists.

        :param mode: Decides which query will be executed.
                    None: both queries will be executed.
                    Antivirus: antivirus query will be executed.
                    Network: network_services query will be executed.
        :param path: Path to json .
        :return: None
        """
        path = f'file:///{path}'

        antivirus_query = "CYPHER 3.5" \
                          "CALL apoc.periodic.iterate(" \
                          "\"CALL apoc.load.json($path) " \
                          "YIELD value " \
                          "UNWIND value.antivirus as entry " \
                          "RETURN entry, value.time AS theTime\", " \
                          "\"MERGE (ipadd:IP {address: entry.ip}) " \
                          "MERGE (softVersion:SoftwareVersion {version: entry.version, tag: 'services_component'}) " \
                          "MERGE (ipadd)<-[:HAS_ASSIGNED]-(nod:Node) " \
                          "WITH softVersion, nod, theTime " \
                          "MERGE (nod)-[:IS_A]->(host:Host) " \
                          "WITH softVersion, host, theTime " \
                          "MERGE (softVersion)-[r:ON]->(host) " \
                          "ON CREATE SET r.start = datetime(theTime),r.end = datetime(theTime) " \
                          "ON MATCH SET r.end = datetime(theTime)\", " \
                          "{batchSize: 1000, iterateList:true, params: {path: {path}}})"

        network_services_query = "CYPHER 3.5" \
                                 "call apoc.periodic.iterate(" \
                                 "\"CALL apoc.load.json($path) " \
                                 "YIELD value " \
                                 "UNWIND value.services as entry " \
                                 "RETURN entry\", " \
                                 "\"MERGE (ipadd:IP {address: entry.ip}) " \
                                 "MERGE (netService:NetworkService { service: entry.service, " \
                                 "tag: \'services_component\', port: entry.port, protocol: entry.protocol}) " \
                                 "MERGE (ipadd)<-[:HAS_ASSIGNED]-(nod:Node) " \
                                 "WITH netService, nod, entry.timestamp AS theTime " \
                                 "MERGE (nod)-[:IS_A]->(host:Host) " \
                                 "WITH netService, host, theTime " \
                                 "MERGE (netService)-[r:ON]->(host) " \
                                 "ON CREATE SET r.start = datetime(theTime),r.end = datetime(theTime) " \
                                 "ON MATCH SET r.end = datetime(theTime)\", " \
                                 "{batchSize: 1000, iterateList:true, params: {path: {path}}})"

        clients_query = "CYPHER 3.5" \
                        "call apoc.periodic.iterate(" \
                        "\"CALL apoc.load.json($path) " \
                        "YIELD value " \
                        "UNWIND value.clients as entry " \
                        "RETURN entry\", " \
                        "\"MERGE (ipclient:IP {address: entry.client}) " \
                        "MERGE (ipserver:IP {address: entry.server}) " \
                        "MERGE (ipclient)<-[:HAS_ASSIGNED]-(nodclient:Node) " \
                        "MERGE (ipserver)<-[:HAS_ASSIGNED]-(nodserver:Node) " \
                        "MERGE (nodclient)-[rel:IS_DEPENDENT_ON {service: entry.service}]->(nodserver) " \
                        "ON CREATE SET rel.last_detected = datetime(entry.timestamp) " \
                        "ON MATCH SET rel.last_detected = datetime(entry.timestamp)\", " \
                        "{batchSize: 1000, iterateList:true, params: {path: {path}}})"

        params = {'path': path}

        if mode is "Antivirus":
            self._run_query(antivirus_query, **params)
            return

        if mode is "Network":
            self._run_query(network_services_query, **params)
            return

        if mode is "Clients":
            self._run_query(clients_query, **params)

        self._run_query(antivirus_query, **params)
        self._run_query(network_services_query, **params)
        self._run_query(clients_query, **params)
