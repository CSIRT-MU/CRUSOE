from neo4j import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://{{ overseer_external_ip }}:7687", auth=basic_auth("neo4j", "{{ vault_neo4j_password }}"))
with(driver.session()) as session:
    session.run("MERGE (ip:IP {address: '{{ firewall_ip }}'}) MERGE (paoNode:PAO {pao: '{{ firewall_pao_name }}', port: {{ firewall_portnumber }}, maxCapacity: {{ firewall_maxCapacity }}, usedCapacity: {{ firewall_usedCapacity }}, freeCapacity: {{ firewall_freeCapacity }}, lastContact: datetime()}) MERGE (paoNode)-[:HAS_ASSIGNED]->(ip) RETURN count(*)")
