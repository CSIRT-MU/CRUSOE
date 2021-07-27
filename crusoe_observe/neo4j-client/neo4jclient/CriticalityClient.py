"""Neo4j client for criticality-estimator component
"""

from neo4jclient.AbsClient import AbstractClient


class CriticalityClient(AbstractClient):
    def __init__(self, password, **kwargs):
        super().__init__(password=password, **kwargs)

    def compute_topology_betweenness(self):
        """
        Compute betweenness centrality on topology edges with hops count equal to 1.

        :return: information about computation
        """
        query = """CALL algo.betweenness(
            'MATCH (n:Node) RETURN id(n) as id',
            'MATCH (s:Node)-[r:IS_CONNECTED_TO]->(t:Node) WHERE r.hops = 1 RETURN id(s) as source, id(t) as target',
            {graph: 'cypher', write: true, writeProperty: 'topology_betweenness'}
        )"""

        return self._run_query(query)

    def compute_topology_degree(self):
        """
        Compute degree centrality on topology edges.

        :return: information about computation
        """
        query = """CALL algo.degree(
            'MATCH (n:Node) RETURN id(n) as id',
            'MATCH (s:Node)-[r:IS_CONNECTED_TO]->(t:Node) RETURN id(s) as source, id(t) as target',
            {graph: 'cypher', write: true, writeProperty: 'topology_degree'}
        )"""

        return self._run_query(query)

    def compute_dependency_degree(self):
        """
        Compute degree centrality on client dependency edges.

        :return: information about computation
        """
        query = """CALL algo.degree(
            'MATCH (n:Node) RETURN id(n) as id',
            'MATCH (s:Node)-[r:IS_DEPENDENT_ON]->(t:Node) RETURN id(s) as source, id(t) as target',
            {graph: 'cypher', write: true, writeProperty: 'dependency_degree'}
        )"""

        return self._run_query(query)
