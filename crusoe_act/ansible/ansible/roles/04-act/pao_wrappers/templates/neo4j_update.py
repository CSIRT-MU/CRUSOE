from neo4j import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://{{ external_ip }}:7687", auth=basic_auth("neo4j", "{{ vault_neo4j_password }}"))
with(driver.session()) as session:
    session.run("MERGE (ip:IP {address: '{{ ip }}'}) MERGE (paoNode:PAO {pao: '{{ pao_name }}', port: {{ portnumber }}, maxCapacity: {{ maxCapacity }}, usedCapacity: {{ usedCapacity }}, freeCapacity: {{ freeCapacity }}, lastContact: datetime()}) MERGE (paoNode)-[:HAS_ASSIGNED]->(ip) RETURN count(*)")
