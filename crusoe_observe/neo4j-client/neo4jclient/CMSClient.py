from neo4jclient.AbsClient import AbstractClient


class CMSClient(AbstractClient):
    def __init__(self, password, **kwargs):
        super().__init__(password=password, **kwargs)

    def get_domain_names(self):
        """
        Gets all domain names from database.

        :return: domain names in JSON-like form
        """
        return self._run_query("MATCH(n:DomainName) RETURN n.domain_name AS domains")

    def get_ips_and_domain_names(self):
        """
        Gets all domain names with corresponding IPs from database.

        :return: IPs and DomainNames in JSON-like form
        """
        return self._run_query("MATCH(n:IP)-[:RESOLVES_TO]-(y:DomainName {tag: \'A/AAAA\'}) "
                               "RETURN { IP: n.address , Domain: y.domain_name } AS entry")

    def create_cms_component(self, path):
        """
        Create nodes and relationships for cms client.
        -------------
        Antivirus_query:
        1. Parse csv given in path.
        2. Create node of type [:SoftwareVersion, :IP] if not already exists.
        3. Create node of type [:Host], relationship of type [:ON] with parameters [start,end] if not already exists.
        Otherwise just update information about time on parameters [start,end].
        4. Create node of type [:Node], relationship of type [:HAS_ASSIGNED].
        5. Create relationship of type [:IS_A] between :Host and :Node if not already exists.

        :param path: Path to the JSON with values
        :return:
        """

        path = f'file:///{path}'

        query = "CALL apoc.load.json($path) " \
                "YIELD value " \
                "UNWIND value.data AS data " \
                "UNWIND data.cpe as cpe " \
                "WITH data.ip as ip_ad, cpe, value.time as theTime " \
                "MERGE (ipadd:IP {address: ip_ad}) " \
                "MERGE (softVersion:SoftwareVersion {version: cpe, tag: \'cms_client\'}) " \
                "MERGE (ipadd)<-[:HAS_ASSIGNED]-(nod:Node) " \
                "MERGE (nod)-[:IS_A]->(host:Host) " \
                "MERGE (softVersion)-[r:ON]->(host) " \
                "ON CREATE SET r.start = datetime(theTime),r.end = datetime(theTime) " \
                "ON MATCH SET r.end = datetime(theTime)"

        params = {'path': path}

        self._run_query(query, **params)
