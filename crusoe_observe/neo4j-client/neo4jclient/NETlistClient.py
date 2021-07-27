from neo4jclient.AbsClient import AbstractClient


class NETlistClient(AbstractClient):
    def __init__(self, password, **kwargs):
        super().__init__(password=password, **kwargs)

    def delete_subnets(self):
        """
        Perform delete on nodes of type :Subnet.
        Used in NETlist_connector.

        :return:
        """
        self._run_query("call apoc.periodic.commit(\""
                        "MATCH (n:Subnet) "
                        "WITH n LIMIT {limit} "
                        "DETACH DELETE n "
                        "RETURN count(*)"
                        "\",{limit:1000})")

    def delete_contacts(self):
        """
        Perform delete on nodes of type: :Contact.

        :return:
        """
        self._run_query("call apoc.periodic.commit(\""
                        "MATCH (n:Contact) "
                        "WITH n LIMIT {limit} "
                        "DETACH DELETE n "
                        "RETURN count(*)"
                        "\",{limit:1000})")

    def delete_NETlist_component(self):
        """
        Delete network layer.

        :return:
        """
        self.delete_subnets()
        self.delete_contacts()

    def get_ips_without_subnet(self):
        """
        Return IPs which are not related to any :Subnet nodes.

        :return: IP addresses
        """
        return self._run_query("MATCH (ip:IP) "
                               "WHERE not (ip)-[:PART_OF]->(:Subnet) "
                               "RETURN ip.address AS ip")

    def create_NETlist_component(self, path):
        """
        Create structure of NETlist component except domain names(see create_NETlist_resolves_to).

        :param path: path to json file with data
        :return:
        """
        path = f'file:///{path}'

        query = "CALL apoc.load.json($path) " \
                "YIELD value " \
                "UNWIND value.subnets as x " \
                "UNWIND x.contacts as contacts WITH x.note AS note, " \
                "x.range AS ran, contacts, x.organization AS organization " \
                "MERGE(o:OrganizationUnit {name: organization}) " \
                "MERGE(n:Contact {name:contacts}) " \
                "MERGE(x:Subnet {range:ran}) ON CREATE SET x.note = note ON MATCH SET x.note = note " \
                "MERGE(x)-[z:HAS]->(n) " \
                "MERGE(x)-[y:PART_OF]->(o) " \
                "RETURN COUNT(*)"

        params = {'path': path}
        self._run_query(query, **params)

    def update_NETlist_component(self, path):
        """
        Update NEtlist component except domain names(see create_NETlist_resolves_to).

        :param path: path to json file with data
        :return:
        """

        path = f'file:///{path}'

        query = "CALL apoc.load.json($path) " \
                "YIELD value " \
                "UNWIND value.collection AS x " \
                "UNWIND x.subnets as subnet " \
                "WITH subnet, x.ip AS ip, x.bestFit AS best " \
                "MATCH(x:IP {address: ip}) " \
                "MATCH(y:Subnet {range: subnet}) " \
                "MERGE (x)-[:PART_OF]->(y) " \
                "FOREACH(ignoreMe IN CASE WHEN subnet = best THEN [1] ELSE [] END | " \
                "MERGE (x)-[z:PART_OF]->(y) ON MATCH SET z.bestFit = True) " \
                "FOREACH(ignoreMe IN CASE WHEN subnet <> best THEN [1] ELSE [] END | " \
                "MERGE (x)-[z:PART_OF]->(y) ON MATCH SET z.bestFit = False) " \
                "RETURN COUNT(*)"

        params = {'path': path}
        self._run_query(query, **params)

    def get_our_subnet_without_domain_name(self):
        return self._run_query("MATCH(n:IP) "
                               "WHERE n.address STARTS WITH '147.251.' "
                               "AND not (n)-[:RESOLVES_TO]-(:DomainName {tag: \'PTR\'}) "
                               "RETURN n.address")

    def create_NETlist_resolves_to(self, path):
        """
        Create domain names and respective relationships.

        :param path: path to json file with data
        :return:
        """

        path = f'file:///{path}'

        query = "CALL apoc.load.json($path) " \
                "YIELD value " \
                "UNWIND value.domains as domain " \
                "MATCH(ip:IP {address: domain.ip}) " \
                "MERGE(dom:DomainName {domain_name: domain.domain, tag: \'PTR\'}) " \
                "MERGE(ip)-[z:RESOLVES_TO]->(dom) " \
                "RETURN count(*)"

        params = {'path': path}
        self._run_query(query, **params)

    def delete_NETlist_resolves_to(self):
        self._run_query("call apoc.periodic.commit(\""
                        "MATCH (n:DomainName {tag: \'PTR\'}) "
                        "WITH n LIMIT {limit} "
                        "DETACH DELETE n "
                        "RETURN count(*)"
                        "\", {limit:1000})")

    # UNUSED
    # def delete_part_of(self):
    #     """
    #     Perform delete on relationships of type :PART_OF.
    #     Big data safety assured by lowering batchSize.
    #     Used in NETlist_connector.
    #     :return:
    #     """
    #     self._run_query("call apoc.periodic.iterate"
    #                     "(\"MATCH (Host)-[p:PART_OF]->(Subnet) RETURN p\","
    #                     " \"DETACH DELETE p\", {batchSize:100}) "
    #                     "yield batches, total "
    #                     "RETURN batches, total")
