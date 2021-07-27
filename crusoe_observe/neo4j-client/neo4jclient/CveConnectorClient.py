from neo4jclient.AbsClient import AbstractClient


class CVEConnectorClient(AbstractClient):
    def __init__(self, password, **kwargs):
        super().__init__(password=password, **kwargs)

    def cve_exists(self, cve_id):
        """
        Checks whether CVE with the specified ID exists in the database.

        :param cve_id: id of CVE
        :return: True if such CVE exists in the database
        """
        record = self._run_query("MATCH (cve:CVE) \
                                  WHERE cve.CVE_id = $cve_id \
                                  RETURN cve.CVE_id",
                                 **{'cve_id': cve_id})
        return record.single() is not None

    def software_version_exists(self, version):
        """
        Checks whether specified software version exists in the database.

        :param version: version of software
        :return: True if such version exists in the database
        """
        record = self._run_query("MATCH (v:SoftwareVersion) \
                                  WHERE v.version = $version \
                                  RETURN v.version",
                                 **{'version': version})
        return record.single() is not None

    def create_new_vulnerability(self, description, vulnerability_type=None):
        """
        Create node of type Vulnerability.

        :param description: description of vulnerability
        :param vulnerability_type: type of vulnerability
        :return:
        """
        self._run_query("CREATE (vul:Vulnerability {description: $description, type: $type})",
                        **{'description': description, 'type': vulnerability_type})

    def create_relationship_between_vulnerability_and_software_version(self, description, version):
        """
        Creates relationship of type :IN between vulnerability and version of software.

        :param description: description of vulnerability
        :param version: version of software
        :return:
        """
        self._run_query("MATCH (vul:Vulnerability), (ver:SoftwareVersion) \
                         WHERE vul.description = $description AND ver.version = $version \
                         MERGE (vul)-[:IN]->(ver)",
                        **{'description': description, 'version': version})

    def create_cve_from_nvd(self, CVE_id, description, access_vector, access_complexity, authentication,
                            confidentiality_impact_v2, integrity_impact_v2, availability_impact_v2, base_score_v2,
                            obtain_all_privilege, obtain_user_privilege, obtain_other_privilege, attack_vector,
                            attack_complexity, privileges_required, user_interaction, scope, confidentiality_impact_v3,
                            integrity_impact_v3, availability_impact_v3, base_score_v3, impact, published_date):
        """
        Creates new node of type CVE.

        :param CVE_id: ID of CVE
        :param description: description of CVE
        :param access_vector: CVSSv2 property Access Vector
        :param access_complexity: CVSSv2 property Access Complexity
        :param authentication: CVSSv2 property Authentication
        :param confidentiality_impact_v2: CVSSv2 property Confidentiality Impact
        :param integrity_impact_v2: CVSSv2 property Integrity Impact
        :param availability_impact_v2: CVSSv2 property Availability Impact
        :param base_score_v2: CVSSv2 property Base Score
        :param obtain_all_privilege: obtainAllPrivilege flag
        :param obtain_user_privilege: obtainUserPrivilege flag
        :param obtain_other_privilege: obtainOtherPrivilege flag
        :param attack_vector: CVSSv3 property Attack Vector
        :param attack_complexity: CVSSv3 property Attack Complexity
        :param privileges_required: CVSSv3 property Privileges Required
        :param user_interaction: CVSSv3 property User Interaction
        :param scope: CVSSv3 property Scope
        :param confidentiality_impact_v3: CVSSv3 property Confidentiality Impact
        :param integrity_impact_v3: CVSSv3 property Integrity Impact
        :param availability_impact_v3: CVSSv3 property Availability Impact
        :param base_score_v3: CVSSv3 property Base Score
        :param impact: impact of a CVE determined by the categorizer
        :param published_date: date when the CVE was published
        :return:
        """
        self._run_query("CREATE (cve:CVE\
                                        {CVE_id: $CVE_ID,\
                                        description: $CVE_description,\
                                        access_vector: $accessVector,\
                                        access_complexity: $accessComplexity,\
                                        authentication: $authentication,\
                                        confidentiality_impact_v2: $conf_impact_v2,\
                                        integrity_impact_v2: $integ_impact_v2,\
                                        availability_impact_v2: $avail_impact_v2,\
                                        base_score_v2: $baseScore_v2,\
                                        obtain_all_privilege: $obtainAllPrivilege,\
                                        obtain_user_privilege: $obtainUserPrivilege,\
                                        obtain_other_privilege: $obtainOtherPrivilege,\
                                        attack_vector: $attackVector,\
                                        attack_complexity: $attackComplexity,\
                                        privileges_required: $privilegesRequired,\
                                        user_interaction: $userInteraction,\
                                        scope: $scope,\
                                        confidentiality_impact_v3: $conf_impact_v3,\
                                        integrity_impact_v3: $integ_impact_v3,\
                                        availability_impact_v3: $avail_impact_v3,\
                                        base_score_v3: $baseScore_v3,\
                                        impact: $impact, \
                                        published_date: $published_date})",
                        **{'CVE_ID': CVE_id,
                           'CVE_description': description,
                           'accessVector': access_vector,
                           'accessComplexity': access_complexity,
                           'authentication': authentication,
                           'conf_impact_v2': confidentiality_impact_v2,
                           'integ_impact_v2': integrity_impact_v2,
                           'avail_impact_v2': availability_impact_v2,
                           'baseScore_v2': base_score_v2,
                           'obtainAllPrivilege': obtain_all_privilege,
                           'obtainUserPrivilege': obtain_user_privilege,
                           'obtainOtherPrivilege': obtain_other_privilege,
                           'attackVector': attack_vector,
                           'attackComplexity': attack_complexity,
                           'privilegesRequired': privileges_required,
                           'userInteraction': user_interaction,
                           'scope': scope,
                           'conf_impact_v3': confidentiality_impact_v3,
                           'integ_impact_v3': integrity_impact_v3,
                           'avail_impact_v3': availability_impact_v3,
                           'baseScore_v3': base_score_v3,
                           'impact': impact,
                           'published_date': published_date})

    def create_relationship_between_cve_and_vulnerability(self, cve_id, vulnerability_description):
        """
        Creates relationship of type "REFERS_TO" between CVE and Vulnerability.

        :param cve_id: id of CVE
        :param vulnerability_description: description of vulnerability
        :return:
        """
        self._run_query("MATCH (cve:CVE), (vul:Vulnerability) \
                         WHERE cve.CVE_id = $cve_id AND vul.description = $description \
                         MERGE (vul)-[:REFERS_TO]->(cve)",
                        **{'cve_id': cve_id, 'description': vulnerability_description})

    def update_cve_from_nvd(self, CVE_id, description, access_vector, access_complexity, authentication,
                            confidentiality_impact_v2, integrity_impact_v2, availability_impact_v2, base_score_v2,
                            obtain_all_privilege, obtain_user_privilege, obtain_other_privilege, attack_vector,
                            attack_complexity, privileges_required, user_interaction, scope, confidentiality_impact_v3,
                            integrity_impact_v3, availability_impact_v3, base_score_v3, impact, published_date):
        """
        Updates node of type CVE.

        :param CVE_id: ID of CVE
        :param description: description of CVE
        :param access_vector: CVSSv2 property Access Vector
        :param access_complexity: CVSSv2 property Access Complexity
        :param authentication: CVSSv2 property Authentication
        :param confidentiality_impact_v2: CVSSv2 property Confidentiality Impact
        :param integrity_impact_v2: CVSSv2 property Integrity Impact
        :param availability_impact_v2: CVSSv2 property Availability Impact
        :param base_score_v2: CVSSv2 property Base Score
        :param obtain_all_privilege: obtainAllPrivilege flag
        :param obtain_user_privilege: obtainUserPrivilege flag
        :param obtain_other_privilege: obtainOtherPrivilege flag
        :param attack_vector: CVSSv3 property Attack Vector
        :param attack_complexity: CVSSv3 property Attack Complexity
        :param privileges_required: CVSSv3 property Privileges Required
        :param user_interaction: CVSSv3 property User Interaction
        :param scope: CVSSv3 property Scope
        :param confidentiality_impact_v3: CVSSv3 property Confidentiality Impact
        :param integrity_impact_v3: CVSSv3 property Integrity Impact
        :param availability_impact_v3: CVSSv3 property Availability Impact
        :param base_score_v3: CVSSv3 property Base Score
        :param impact: impact of a CVE determined by the categorizer
        :param published_date: date when the CVE was published
        :return:
        """
        self._run_query("MATCH (cve:CVE {CVE_id: $CVE_ID})\
                                        SET cve.description = $CVE_description,\
                                        cve.access_vector = $accessVector,\
                                        cve.access_complexity = $accessComplexity,\
                                        cve.authentication = $authentication,\
                                        cve.confidentiality_impact_v2 = $conf_impact_v2,\
                                        cve.integrity_impact_v2 = $integ_impact_v2,\
                                        cve.availability_impact_v2 = $avail_impact_v2,\
                                        cve.base_score_v2 = $baseScore_v2,\
                                        cve.obtain_all_privilege = $obtainAllPrivilege,\
                                        cve.obtain_user_privilege = $obtainUserPrivilege,\
                                        cve.obtain_other_privilege = $obtainOtherPrivilege,\
                                        cve.attack_vector = $attackVector,\
                                        cve.attack_complexity = $attackComplexity,\
                                        cve.privileges_required = $privilegesRequired,\
                                        cve.user_interaction = $userInteraction,\
                                        cve.scope = $scope,\
                                        cve.confidentiality_impact_v3 = $conf_impact_v3,\
                                        cve.integrity_impact_v3 = $integ_impact_v3,\
                                        cve.availability_impact_v3 = $avail_impact_v3,\
                                        cve.base_score_v3 = $baseScore_v3,\
                                        cve.impact = $impact, \
                                        cve.published_date = $published_date",
                        **{'CVE_ID': CVE_id,
                           'CVE_description': description,
                           'accessVector': access_vector,
                           'accessComplexity': access_complexity,
                           'authentication': authentication,
                           'conf_impact_v2': confidentiality_impact_v2,
                           'integ_impact_v2': integrity_impact_v2,
                           'avail_impact_v2': availability_impact_v2,
                           'baseScore_v2': base_score_v2,
                           'obtainAllPrivilege': obtain_all_privilege,
                           'obtainUserPrivilege': obtain_user_privilege,
                           'obtainOtherPrivilege': obtain_other_privilege,
                           'attackVector': attack_vector,
                           'attackComplexity': attack_complexity,
                           'privilegesRequired': privileges_required,
                           'userInteraction': user_interaction,
                           'scope': scope,
                           'conf_impact_v3': confidentiality_impact_v3,
                           'integ_impact_v3': integrity_impact_v3,
                           'avail_impact_v3': availability_impact_v3,
                           'baseScore_v3': base_score_v3,
                           'impact': impact,
                           'published_date': published_date})

    def get_cve_patch(self, CVE_id):
        """
        Return boolean value for CVE property 'patched'.

        :param CVE_id: ID of CVE
        :return:
        """
        record = self._run_query("MATCH (node:CVE) \
                                WHERE node.CVE_id = $CVE_id \
                                RETURN node.patched",
                                 **{'CVE_id': CVE_id})
        data = record.single()
        if data is None:
            return None
        return data['node.patched']

    def get_cve(self, CVE_id):
        """
        Return CVE with specified id.

        :param CVE_id: id of CVE
        :return:
        """
        return self._run_query("MATCH (cve:CVE) \
                         WHERE cve.CVE_id = $CVE_id \
                         RETURN {description: cve.description, CVE_id: cve.CVE_id, \
                                published_date: cve.published_date} AS cve",
                               **{'CVE_id': CVE_id})

    def update_cve_from_vendor(self, CVE_id, patched, description, published_date):
        """
        Updates CVE according to the data acquired from the vendors.

        :param CVE_id: ID of CVE
        :param patched: boolean value describing whether a patch is available
        :param description: description of CVE by a vendor
        :param published_date: date when CVE was published
        :return:
        """
        self._run_query("MATCH (cve:CVE {CVE_id: $CVE_id}) \
                    SET cve.patched = $patched, \
                    cve.vendor_description = $description, \
                    cve.published_date = $published_date",
                        **{'CVE_id': CVE_id, 'patched': patched, 'description': description,
                           'published_date': published_date})

    def get_versions_of_product(self, vendor_and_product):
        """
        Get all software versions in the DB which have the same vendor and product name.

        :param vendor_and_product: vendor and product name of software
        :return:
        """
        product_string = vendor_and_product + ":"
        return self._run_query("MATCH (s:SoftwareVersion) WHERE s.version STARTS WITH $product_string "
                               "RETURN {version: s.version} AS software",
                               **{'product_string': product_string}).data()
