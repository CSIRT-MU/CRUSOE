from neo4jclient.AbsClient import AbstractClient
import json


class RESTClient(AbstractClient):
    def __init__(self, password, **kwargs):
        super().__init__(password=password, **kwargs)

    "---------------------------------------------PAO--------------------------------------------------------"

    def create_pao(self, paos):
        """
        Create paos from given json.

        :param paos: JSON with paos
        :return: None
        """
        query = "WITH apoc.convert.fromJsonMap($paos) as value " \
                "UNWIND value.pao_init as entry " \
                "WITH entry.port as port, entry.usedCapacity as usedCapacity, entry.ip as IP, " \
                "entry.maxCapacity as maxCapacity, entry.freeCapacity as freeCapacity, " \
                "entry.pao as pao, entry.lastContact as lastContact " \
                "MERGE (ip:IP {address: IP}) " \
                "MERGE (paoNode:PAO {pao: pao, port: port, maxCapacity: maxCapacity, usedCapacity: usedCapacity, " \
                "freeCapacity: freeCapacity, lastContact: lastContact}) " \
                "MERGE (paoNode)-[:HAS_ASSIGNED]->(ip) " \
                "RETURN count(*)"

        params = {'paos': paos}

        self._run_query(query, **params)

    def get_all_paos(self, limit):
        """
        Return all paos.

        :param limit: self explanatory
        :return:
        """

        query = "MATCH (n:PAO)-[:HAS_ASSIGNED]->(x:IP) " \
                "WITH n.pao as name, n.port as port, x.address as ip " \
                "WITH {pao:name, port:port, ip:ip} as json " \
                "LIMIT $limit " \
                "WITH apoc.convert.toJson(json) as x " \
                "WITH {paos:collect(apoc.convert.fromJsonMap(x))} as result " \
                "RETURN result"

        params = {'limit': limit}

        result = self._run_query(query, **params)
        return result.value()[0]

    def get_last_contact_pao(self, pao):
        """
        Get lastContact of given pao.

        :param pao: name of pao
        :return:
        """
        result = self._run_query("MATCH (n:PAO {pao: $pao}) RETURN {lastContact:toString(n.lastContact)}", **{'pao': pao})
        return result.value()[0]

    def get_max_capacity_pao(self, pao):
        """
        Get maxCapacity of given pao.

        :param pao: name of pao
        :return:
        """
        result = self._run_query("MATCH (n:PAO {pao: $pao}) RETURN {maxCapacity:n.maxCapacity}", **{'pao': pao})
        return result.value()[0]

    def get_used_capacity_pao(self, pao):
        """
        Get usedCapacity of given pao.

        :param pao: name of pao
        :return:
        """
        result = self._run_query("MATCH (n:PAO {pao: $pao}) RETURN {usedCapacity:n.usedCapacity}", **{'pao': pao})
        return result.value()[0]

    def get_free_capacity_pao(self, pao):
        """
        Get freeCapacity of given pao.

        :param pao: name of pao
        :return:
        """
        result = self._run_query("MATCH (n:PAO {pao: $pao}) RETURN {freeCapacity:n.freeCapacity}", **{'pao': pao})
        return result.value()[0]

    def set_max_capacity_pao(self, pao, capacity):
        """
        Set maxCapacity of given pao.

        :param pao: name of pao
        :param capacity: capacity
        :return:
        """
        return self._run_query("MATCH (n:PAO {pao:$pao}) SET n.maxCapacity = $capacity",
                               **{'pao': pao, 'capacity': capacity})

    def set_free_capacity_pao(self, pao, capacity):
        """
        Set maxCapacity of given pao.

        :param pao: name of pao
        :param capacity: capacity
        :return:
        """
        return self._run_query("MATCH (n:PAO {pao:$pao}) SET n.freeCapacity = $capacity",
                               **{'pao': pao, 'capacity': capacity})

    def set_used_capacity_pao(self, pao, capacity):
        """
        Set maxCapacity of given pao.

        :param pao: name of pao
        :param capacity: capacity
        :return:
        """
        return self._run_query("MATCH (n:PAO {pao:$pao}) SET n.usedCapacity = $capacity",
                               **{'pao': pao, 'capacity': capacity})

    def set_last_contact_pao(self, pao, time):
        """
        Set maxCapacity of given pao.

        :param pao: name of pao
        :param time: time
        :return:
        """
        return self._run_query("MATCH (n:PAO {pao:$pao}) SET n.lastContact = datetime($time)",
                               **{'pao': pao, 'time': time})

    def delete_pao(self):
        """
        Delete all paos.

        :return: None
        """
        query = "MATCH(n:PAO) DETACH DELETE(n)"

        self._run_query(query)

    def update_pao_liveliness_status(self):
        """
        Update liveliness status of pao nodes.

        :return: None
        """
        query = "MATCH(n:PAO) " \
                "WITH duration.inSeconds(datetime(n.lastContact), datetime()).seconds as liveliness, n " \
                "CALL apoc.do.case(" \
                "[liveliness > 1800, \"MATCH(n) SET n.liveliness_status=\'Unreachable\'\", " \
                "liveliness > 600, \"MATCH(n) SET n.liveliness_status=\'Last liveness check failed\'\"], " \
                "\"MATCH(n) SET n.liveliness_status=\'OK\'\", {liveliness:liveliness, n:n}) " \
                "yield value " \
                "RETURN value"

        self._run_query(query)

    def update_pao_capacity_status_special(self):
        """
        Update capacity status of pao nodes where maxCap = 0.

        :return: None
        """
        query = "MATCH(n:PAO) " \
                "WHERE n.maxCapacity = 0 " \
                "SET n.capacity_status=\'Capacity full\'"

        self._run_query(query)

    def update_pao_capacity_status(self):
        """
        Update capacity status of pao nodes.

        :return: None
        """
        query = "MATCH(n:PAO) " \
                "WHERE n.maxCapacity <> 0 " \
                "WITH toFloat(n.usedCapacity) / n.maxCapacity as capacity, n " \
                "CALL apoc.do.case(" \
                "[capacity >= 1, \"MATCH(n) SET n.capacity_status=\'Capacity full\'\", " \
                "capacity >= 0.9, \"MATCH(n) SET n.capacity_status=\'Capacity 90 % full\'\"], " \
                "\"MATCH(n) SET n.capacity_status=\'OK\'\", {capacity:capacity, n:n}) " \
                "yield value " \
                "RETURN value"

        self._run_query(query)

    def get_liveliness_status_pao(self, pao):
        """
        Get liveliness_status of given pao.

        :param pao: name of pao
        :return:
        """
        result = self._run_query("MATCH (n:PAO {pao: $pao}) RETURN n.liveliness_status", **{'pao': pao})
        return result.value()[0]

    def get_capacity_status_pao(self, pao):
        """
        Get capacity_status of given pao.

        :param pao: name of pao
        :return:
        """
        result = self._run_query("MATCH (n:PAO {pao: $pao}) RETURN n.capacity_status", **{'pao': pao})
        return result.value()[0]

    "______________________________________YELLOW LAYER_____________________________________________________"

    def get_all_organization_units(self, limit):
        """
        Get all organization unit from the database up to limit {limit}.

        :param limit: self explanatory
        :return:
        """
        return self._run_query("MATCH (org:OrganizationUnit) \
                                RETURN {name: org.name} AS organization LIMIT $limit", **{'limit': limit})

    def organization_unit_exists(self, name):
        """
        Checks whether organization unit with the specified name exists in the database.

        :param name: name of the organization unit
        :return: True if such organization unit exists in the database
        """
        record = self._run_query("MATCH (o:OrganizationUnit) \
                                  WHERE o.name = $name \
                                  RETURN o.name",
                                 **{'name': name})
        return record.single() is not None

    def get_organization_unit_subnets(self, organization_unit, limit):
        """
        Return subnets which are under specified organization unit up to limit {limit}.

        :param organization_unit: self explanatory
        :param limit: self explanatory
        :return: subnets in JSON-like form
        """
        return self._run_query("MATCH (org:OrganizationUnit {name: $name})<-[:PART_OF]-(subnets:Subnet) \
                                RETURN subnets.range, subnets.note AS subnets LIMIT $limit",
                               **{'name': organization_unit, 'limit': limit})

    "______________________________________PURPLE LAYER_____________________________________________________"

    def get_all_cve(self, limit):
        """
        Returns all CVEs that are in the database up to limit {limit}.

        :param limit: self explanatory
        :return: CVEs
        """
        return self._run_query("MATCH (cve:CVE) RETURN {description: cve.description, CVE_id: cve.CVE_id} AS cve "
                               "LIMIT $limit", **{'limit': limit})

    def cve_exists(self, cve_id):
        """
        Checks whether CVE with specified id exists in the database.

        :param cve_id: self-explanatory
        :return: True if such subnet exists in the database
        """
        record = self._run_query("MATCH (cve:CVE) \
                                  WHERE cve.CVE_id = $cve_id \
                                  RETURN cve",
                                 **{'cve_id': cve_id})
        return record.single() is not None

    def get_cve(self, cve_id):
        """
        Returns CVE with given id.

        :param cve_id: self-explanatory
        :return: CVE with all the details
        """
        return self._run_query("MATCH (cve:CVE {CVE_id: $cve_id}) RETURN cve", **{'cve_id': cve_id})

    def get_all_ip_with_cve(self, cve_id, limit):
        """
        Returns IPs which are connected to CVE.

        :param limit: self explanatory
        :param cve_id: self-explanatory
        :return: IPs
        """
        return self._run_query("MATCH (cve:CVE {CVE_id: $cve_id})<-[:REFERS_TO]-(vuln:Vulnerability)"
                               "WITH vuln "
                               "MATCH (vuln)-[:IN]->(soft:SoftwareVersion) "
                               "WITH soft "
                               "MATCH (soft)-[r:ON]->(host:Host) "
                               "WHERE r.end > datetime() - duration('PT45M') "
                               "OR r.start > datetime() - duration('PT45M') "
                               "WITH host "
                               "MATCH (host)<-[:IS_A]-(nod:Node)-[:HAS_ASSIGNED]->(ip:IP) "
                               "RETURN DISTINCT(ip) LIMIT $limit", **{'cve_id': cve_id, 'limit': limit})

    "______________________________________RED LAYER_____________________________________________________"

    def get_all_mission(self, limit):
        """
        Returns all missions from the database.

        :param limit: self explanatory
        :return: Missions
        """
        result = self._run_query("MATCH (m:Mission) RETURN {name: m.name, description: m.description, \
                                criticality: m.criticality, \
                                structure: m.structure} AS mission LIMIT $limit",
                               **{'limit': limit})

        return result.value()

    def create_mission(self, mission_name, description, criticality, data):
        """
        Creates node of type: mission.

        :param mission_name: name of mission
        :param description: description of mission
        :param criticality: criticality of mission
        :param data: structure of mission (graph)
        :return:
        """
        self._run_query("MERGE (m:Mission {name: $name, description: $description, criticality: $mission_criticality, \
                         structure: $data})",
                        **{'name': mission_name, 'description': description, 'mission_criticality': criticality,
                           'data': data})

    def create_missions_and_components_string(self, result):
        """
        Cypher for creating missions,components, additional required nodes and relationships directly from JSON-string.

        :param result: JSON result
        :return: None
        """
        query = "WITH apoc.convert.fromJsonMap($result) as value " \
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

        params = {'result': result}

        self._run_query(query, **params)

    def get_mission_details(self, mission_name):
        """
        Retrieve details about mission (i.e., name, description, criticality, structure).

        :param mission_name: name of mission
        :return: details about the mission
        """
        result = self._run_query("MATCH (m:Mission) WHERE m.name=$mission_name "
                               "RETURN {name: m.name, description: m.description, criticality: m.criticality, \
                               structure: m.structure} AS mission",
                               **{'mission_name': mission_name})
        return result.value()[0]

    def mission_exists(self, name):
        """
        Checks whether mission with the specified name exists in the database.

        :param name: name of the mission
        :return: True if such mission exists
        """
        record = self._run_query("MATCH (m:Mission) \
                                  WHERE m.name = $name \
                                  RETURN m.name",
                                 **{'name': name})
        return record.single() is not None

    def delete_mission(self, name):
        """
        Delete mission with specified name.

        :param name: name of the mission
        :return: True if such mission exists
        """
        return self._run_query("MATCH (m:Mission) \
                                  WHERE m.name = $name \
                                  DETACH DELETE m",
                               **{'name': name})

    def get_mission_configurations(self, name):
        """
        Returns representation of all configurations related to the mission.

        :param name: name of mission
        :return:
        """
        return self._run_query(
            'MATCH (m:Mission {name: $name})-[:HAS]->(c:Configuration) RETURN {config_id: c.config_id, \
             confidentiality: c.confidentiality, integrity: c.integrity, availability: c.availability, \
             time: c.time} AS configuration', **{'name': name}).data()

    def get_mission_hosts(self, name):
        """
        Returns representation of all hosts related to the mission.

        :param name: name of mission
        :return:
        """
        mission_data = self._run_query('MATCH (m:Mission {name: $name}) RETURN m.structure AS structure',
                                       **{'name': name}).single().data()['structure']
        mission_json = json.loads(mission_data)
        hosts = mission_json['nodes']['hosts']
        return hosts

    def get_configuration(self, mission, config_id):
        """
        Returns representation of the specified configuration.

        :param mission: name of the mission
        :param config_id: ID of the configuration for the specificied mission
        :return:
        """
        return self._run_query(
            'MATCH (:Mission {name: $name})-[:HAS]->(c:Configuration {config_id: $config_id})-[r:CONTAINS]->(h:Host)<-[:IS_A]-(:Node)-[:HAS_ASSIGNED]->(ip:IP) \
             RETURN {confidentiality: r.confidentiality, integrity: r.integrity, availability: r.availability, \
             ip_address: ip.address, hostname: h.hostname} as host', **{'name': mission, 'config_id': config_id}).data()

    def get_missions_hosts_evaluation(self):
        """
        Returns all hosts which belong to the misions together with their worst-case evaluation in one of the missions.
        Evaluation is a tuple consisting of probability for confidentiality, integrity and availability.

        :return:
        """
        return self._run_query(
            "MATCH (n:Mission)-[:HAS]->(:Configuration)-[c:CONTAINS]->(h:Host)<-[:IS_A]-(:Node)-[:HAS_ASSIGNED]->(ip:IP) \
             RETURN {conf: max(c.confidentiality), integ: max(c.integrity), avail: max(c.availability), \
             hostname: h.hostname, ip_address: ip.address} as host").data()

    "______________________________________LIGHT BLUE LAYER_____________________________________________________"

    def get_all_ips(self, limit):
        """
        Get all IPs from database up to limit {limit}.

        :param limit: self explanatory
        :return: IPs
        """
        return self._run_query("MATCH (ip:IP) RETURN ip LIMIT $limit", **{'limit': limit})

    def ip_exists(self, ip):
        """
        Checks whether ip with specified address exists in the database.

        :param ip: ip address
        :return: True if such ip exists
        """
        record = self._run_query("MATCH (ip:IP) WHERE ip.address = $ip RETURN ip.address", **{'ip': ip})
        return record.single() is not None

    def get_ip_details(self, ip):
        """
        Get details about given IP from the database (domain_name, subnet, org_unit, contact).

        :param ip: checked ip
        :return: Details
        """
        return self._run_query("MATCH (ip:IP) "
                               "WHERE ip.address = $ip "
                               "WITH ip "
                               "MATCH (ip)-[:PART_OF]->(subnet:Subnet)-[:HAS]->(contact:Contact) "
                               "OPTIONAL MATCH (ip)-[:RESOLVES_TO]->(domain:DomainName) "
                               "WITH ip, subnet, domain, contact "
                               "OPTIONAL MATCH (subnet)-[:PART_OF]->(org:OrganizationUnit)"
                               "RETURN {subnet: collect(DISTINCT(subnet))"
                               ", contact: collect(DISTINCT(contact))"
                               ", domain_name: collect(DISTINCT(domain))"
                               ", organization: collect(DISTINCT(org))} AS details", **{'ip': ip})

    def get_ip_sec_events(self, ip, limit):
        """
        Get all security events related to given IP.

        :param ip: checked ip
        :param limit: self explanatory
        :return: Sec. events
        """
        return self._run_query("MATCH (ip:IP {address: $ip})-[:SOURCE_OF]->(sec:SecurityEvent) "
                               "RETURN {time: toString(sec.detection_time)"
                               ", type: sec.type"
                               ", description: sec.description"
                               ", confirmed: sec.confirmed} AS event "
                               "ORDER BY event.time desc LIMIT $limit", **{'ip': ip, 'limit': limit})

    def get_ip_active_events(self, ip, limit):
        """
        Get last detected events from every type of events related to given IP.

        :param ip: checked ip
        :param limit: self explanatory
        :return: Sec. events
        """
        return self._run_query("MATCH (ip:IP {address: $ip})-[:SOURCE_OF]->(sec:SecurityEvent) "
                               "WITH date({year:sec.detection_time.year"
                               ", month:sec.detection_time.month"
                               ", day:sec.detection_time.day}) as last, sec.type as threat "
                               "WITH threat, max(last) as last "
                               "MATCH (ip:IP {address: $ip})-[:SOURCE_OF]->(sec:SecurityEvent {type: threat}) "
                               "WHERE last = date(sec.detection_time) "
                               "RETURN {time: toString(sec.detection_time)"
                               ", type: sec.type"
                               ", description: sec.description"
                               ", confirmed: sec.confirmed} AS event", **{'ip': ip, 'limit': limit})

    def get_ip_date_events(self, ip, date, limit):
        """
        Get all events which happened on date <date> and are related to ip <ip> up to limit <limit>.

        :param ip: checked ip
        :param date: date
        :param limit: limit
        :return: Sec. events
        """
        if len(date) == 4:  # only year provided
            return self._run_query("MATCH (ip:IP {address: $ip})-[:SOURCE_OF]->(sec:SecurityEvent) "
                                   "WHERE sec.detection_time.year = date($date).year "
                                   "RETURN {time: toString(sec.detection_time)"
                                   ", type: sec.type"
                                   ", description: sec.description"
                                   ", confirmed: sec.confirmed} AS event "
                                   "LIMIT $limit", **{'ip': ip, 'date': date, 'limit': limit})
        elif len(date) == 7:  # only year and month provided
            return self._run_query("MATCH (ip:IP {address: $ip})-[:SOURCE_OF]->(sec:SecurityEvent) "
                                   "WHERE sec.detection_time.year = date($date).year "
                                   "AND sec.detection_time.month = date($date).month "
                                   "RETURN {time: toString(sec.detection_time)"
                                   ", type: sec.type"
                                   ", description: sec.description"
                                   ", confirmed: sec.confirmed} AS event "
                                   "LIMIT $limit", **{'ip': ip, 'date': date, 'limit': limit})

        return self._run_query("MATCH (ip:IP {address: $ip})-[:SOURCE_OF]->(sec:SecurityEvent) "
                               "WHERE sec.detection_time.year = date($date).year "
                               "AND sec.detection_time.month = date($date).month "
                               "AND sec.detection_time.day = date($date).day "
                               "RETURN {time: toString(sec.detection_time)"
                               ", type: sec.type"
                               ", description: sec.description"
                               ", confirmed: sec.confirmed} AS event "
                               "LIMIT $limit", **{'ip': ip, 'date': date, 'limit': limit})

    def get_ip_services(self, ip, limit):
        """
        Get all services connected to ip <ip> up to limit <limit>.

        :param ip: self explanatory
        :param limit: self explanatory
        :return: Services
        """
        return self._run_query("MATCH (ip:IP {address: $ip})<-[:HAS_ASSIGNED]-(nod:Node)-[:IS_A]->(host:Host) "
                               "WITH host "
                               "OPTIONAL MATCH (host)<-[:ON]-(net:NetworkService) "
                               "RETURN net LIMIT $limit", **{'ip': ip, 'limit': limit})

    def get_ip_software(self, ip, limit):
        """
        Get all services connected to ip <ip> up to limit <limit>.

        :param ip: self explanatory
        :param limit: self explanatory
        :return: Services
        """
        return self._run_query("MATCH (ip:IP {address: $ip})<-[:HAS_ASSIGNED]-(nod:Node)-[:IS_A]->(host:Host) "
                               "WITH host "
                               "OPTIONAL MATCH (host)<-[:ON]-(soft:SoftwareVersion) "
                               "RETURN DISTINCT(soft) "
                               "LIMIT $limit", **{'ip': ip, 'limit': limit})

    def get_ip_cve(self, ip, limit):
        """
        Returns all CVE related to ip <ip> up to limit <limit>.

        :param ip: ip
        :param limit: limit
        :return: CVEs
        """
        return self._run_query("MATCH (ip:IP {address: $ip})<-[:HAS_ASSIGNED]-(nod:Node)-[:IS_A]-(host:Host) "
                               "WITH host "
                               "MATCH (host)<-[:ON]-(soft:SoftwareVersion)<-[:IN]-(vul:Vulnerability)-[:REFERS_TO]->(cve:CVE) "
                               "RETURN cve LIMIT $limit", **{'ip': ip, 'limit': limit})

    def subnet_exists(self, subnet):
        """
        Checks whether subnet exists in database.

        :param subnet: self explanatory
        :return: Details
        """
        record = self._run_query("MATCH (subnet:Subnet) "
                                 "WHERE subnet.range = $subnet RETURN subnet", **{'subnet': subnet})
        return record.single() is not None

    def get_subnets(self, limit):
        """
        Returns all subnets up to limit <limit>.

        :param limit: self explanatory
        :return: Subnets
        """
        return self._run_query("MATCH (subnet:Subnet) RETURN subnet LIMIT $limit", **{'limit': limit})

    def get_subnets_details(self, subnet):
        """
        Returns detailed info about subnet (it's contact and organization unit).

        :param subnet: self explanatory
        :return: Subnet Details
        """
        return self._run_query("MATCH (subnet:Subnet {range: $subnet}) "
                               "WITH subnet "
                               "OPTIONAL MATCH (subnet)-[:PART_OF]->(org:OrganizationUnit) "
                               "OPTIONAL MATCH (subnet)-[:HAS]-(contact:Contact) "
                               "RETURN {contact: collect(DISTINCT(contact))"
                               ", organization: collect(DISTINCT(org))} AS details ", **{'subnet': subnet})

    def get_subnet_ips(self, subnet, limit):
        """
        Returns ip's under subnet <subnet> up to limit <limit>.

        :param subnet: self explanatory
        :param limit: self explanatory
        :return: Ips
        """
        return self._run_query("MATCH (subnet:Subnet {range: $subnet})<-[:PART_OF]-(ip:IP) "
                               "RETURN DISTINCT(ip) LIMIT $limit", **{'subnet': subnet, 'limit': limit})

    "____________________________________________GREEN LAYER________________________________________________________"

    def get_software_resources(self, limit):
        """
        Get software resources up to limit <limit>.

        :param limit: self explanatory
        :return: Software resources
        """
        return self._run_query("MATCH (soft:SoftwareVersion) RETURN soft LIMIT $limit", **{'limit': limit})

    def software_exists(self, software):
        """
        Checks whether given software exists in database.

        :param software: to be checked
        :return: True if software is in database, false otherwise
        """
        record = self._run_query("MATCH (soft:SoftwareVersion) "
                                 "WHERE soft.version = $software RETURN soft.version", **{'software': software})
        return record.single() is not None

    def get_software_ips(self, software, limit):
        """
        Get all ips which has software <software> up to limit <limit>.

        :param software: self explanatory
        :param limit: self explanatory
        :return: IPs
        """
        return self._run_query("MATCH(soft:SoftwareVersion {version: $software})-[:ON]->(host:Host)<-[:IS_A]-(node:Node)-[:HAS_ASSIGNED]->(ip:IP) "
                               "RETURN ip LIMIT $limit", **{'software': software, 'limit': limit})

    def get_network_services(self, limit):
        """
        Get network services up to limit <limit>.

        :param limit: self explanatory
        :return: Network Services
        """
        return self._run_query("MATCH (service:NetworkService) RETURN service LIMIT $limit", **{'limit': limit})

    def network_service_exists(self, service):
        """
        Checks whether service <service> exists.

        :param service: checked entity
        :return: True if service is in database, false otherwise
        """
        record = self._run_query("MATCH (serv:NetworkService) "
                                 "WHERE serv.service = $service RETURN serv.service", **{'service': service})
        return record.single() is not None

    def get_network_service_details(self, service):
        """
        Get details of network service <service>.

        :param service: self explanatory
        :return: Service details
        """
        return self._run_query("MATCH(serv:NetworkService { service: $service}) "
                               "RETURN {name: serv.service, tag: serv.tag, port: serv.port, protocol: serv.protocol}",
                               **{'service': service})

    def get_network_service_ips(self, service, limit):
        """
        Get all ips which has network service <service> up to limit <limit>.

        :param service: checked entity
        :param limit: self explanatory
        :return: IPs
        """
        return self._run_query("MATCH(serv:NetworkService {service: $service})-[:ON]->(host:Host)<-[:IS_A]-(node:Node)-[:HAS_ASSIGNED]->(ip:IP) "
            "RETURN ip LIMIT $limit", **{'service': service, 'limit': limit})

    "____________________________________________ORANGE LAYER________________________________________________________"

    def get_all_events(self, limit):
        """
        Get security events up to limit <limit>.

        :param limit: self explanatory
        :return: Security events
        """
        return self._run_query("MATCH(sec:SecurityEvent) "
                               "RETURN {time: toString(sec.detection_time)"
                               ", type: sec.type"
                               ", description: sec.description"
                               ", confirmed: sec.confirmed} AS event ORDER BY sec.detection_time desc "
                               "LIMIT $limit", **{'limit': limit})

    def get_events_after_date(self, date, limit):
        """
        Get security events detected after date <date> up to limit <limit>.

        :param date: self explanatory
        :param limit: self explanatory
        :return: Security events
        """
        if len(date) == 4:  # only year provided
            return self._run_query("MATCH (sec:SecurityEvent) "
                                   "WHERE sec.detection_time.year >= date($date).year "
                                   "RETURN {time: toString(sec.detection_time)"
                                   ", type: sec.type"
                                   ", description: sec.description"
                                   ", confirmed: sec.confirmed} AS event ORDER BY sec.detection_time desc "
                                   "LIMIT $limit", **{'date': date, 'limit': limit})
        elif len(date) == 7:  # only year and month provided
            return self._run_query("MATCH (sec:SecurityEvent) "
                                   "WHERE sec.detection_time.year >= date($date).year "
                                   "AND sec.detection_time.month >= date($date).month "
                                   "RETURN {time: toString(sec.detection_time)"
                                   ", type: sec.type"
                                   ", description: sec.description"
                                   ", confirmed: sec.confirmed} AS event ORDER BY sec.detection_time desc "
                                   "LIMIT $limit", **{'date': date, 'limit': limit})

        return self._run_query("MATCH (sec:SecurityEvent) "
                               "WHERE sec.detection_time.year >= date($date).year "
                               "AND sec.detection_time.month >= date($date).month "
                               "AND sec.detection_time.day >= date($date).day "
                               "RETURN {time: toString(sec.detection_time)"
                               ", type: sec.type"
                               ", description: sec.description"
                               ", confirmed: sec.confirmed} AS event ORDER BY sec.detection_time desc "
                               "LIMIT $limit", **{'date': date, 'limit': limit})

    def get_events_by_date(self, date, limit):
        """
        Get security events detected on date <date> up to limit <limit>.

        :param date: self explanatory
        :param limit: self explanatory
        :return: Security events
        """
        if len(date) == 4:  # only year provided
            return self._run_query("MATCH (sec:SecurityEvent) "
                                   "WHERE sec.detection_time.year = date($date).year "
                                   "RETURN {time: toString(sec.detection_time)"
                                   ", type: sec.type"
                                   ", description: sec.description"
                                   ", confirmed: sec.confirmed} AS event ORDER BY sec.detection_time desc "
                                   "LIMIT $limit", **{'date': date, 'limit': limit})
        elif len(date) == 7:  # only year and month provided
            return self._run_query("MATCH (sec:SecurityEvent) "
                                   "WHERE sec.detection_time.year = date($date).year "
                                   "AND sec.detection_time.month = date($date).month "
                                   "RETURN {time: toString(sec.detection_time)"
                                   ", type: sec.type"
                                   ", description: sec.description"
                                   ", confirmed: sec.confirmed} AS event ORDER BY sec.detection_time desc "
                                   "LIMIT $limit", **{'date': date, 'limit': limit})

        return self._run_query("MATCH (sec:SecurityEvent) "
                               "WHERE sec.detection_time.year = date($date).year "
                               "AND sec.detection_time.month = date($date).month "
                               "AND sec.detection_time.day = date($date).day "
                               "RETURN {time: toString(sec.detection_time)"
                               ", type: sec.type"
                               ", description: sec.description"
                               ", confirmed: sec.confirmed} AS event ORDER BY sec.detection_time desc "
                               "LIMIT $limit", **{'date': date, 'limit': limit})