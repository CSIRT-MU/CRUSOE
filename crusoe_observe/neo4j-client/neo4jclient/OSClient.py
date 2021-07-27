#!/usr/bin/python3.6
from neo4jclient.AbsClient import AbstractClient


class OSClient(AbstractClient):
    def __init__(self, password, **kwargs):
        super().__init__(password=password, **kwargs)

    def upload_os_from_file(self, path='/var/lib/neo4j/import/os.json'):
        """
        Create required cypher query for uploading data to database.

        :param path: path to json file with data which will be uploaded.
        new - only add new data with HAS_OS relationship.
        inactive - don't touch HAS_OS relationship.
        changed - update new OS.
        unchanged - update only time, not OS.
        :return: None.
        """

        path = f'file:///{path}'

        change_query = "CYPHER 3.5 " \
                       "CALL apoc.periodic.iterate(\"" \
                       "CALL apoc.load.json($path) " \
                       "YIELD value UNWIND (value.new + value.changed) AS entry " \
                       "RETURN entry, value.start_time AS stime, value.end_time AS etime\", \"" \
                       "MERGE (ipadd:IP {address:entry.ip}) " \
                       "MERGE (soft:SoftwareVersion {version: entry.os, tag: \'os_component\'}) " \
                       "MERGE (ipadd)<-[:HAS_ASSIGNED]-(nod:Node) " \
                       "WITH soft, stime, etime, nod " \
                       "MERGE (nod)-[:IS_A]->(host:Host) " \
                       "WITH soft, stime, etime, host " \
                       "CREATE (soft)-[:ON {start:datetime(stime), end:datetime(etime)}]->(host)\", " \
                       "{batchSize: 400, iterateList:true, params: {path: {path}}})"

        unchange_query = 'CYPHER 3.5' \
                         'CALL apoc.load.json($path) ' \
                         'YIELD value ' \
                         'UNWIND (value.unchanged) AS entry ' \
                         'MATCH (soft:SoftwareVersion {version: entry.os, tag: \'os_component\'})-[o:ON]->(:Host)<-' \
                         '[:IS_A]-(:Node)-[:HAS_ASSIGNED]->(ip:IP {address:entry.ip}) ' \
                         'WITH max(o.end) as maxO, entry, value ' \
                         'MATCH (:SoftwareVersion {version: entry.os, tag: \'os_component\'})-[o2:ON]->(:Host)<-' \
                         '[:IS_A]-(:Node)-[:HAS_ASSIGNED]->(:IP {address:entry.ip}) ' \
                         'WHERE o2.end = maxO ' \
                         'SET o2.end = datetime(value.end_time) ' \
                         'RETURN \"success\"'

        params = {'path': path}
        self._run_query(change_query, **params)
        self._run_query(unchange_query, **params)
