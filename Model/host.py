from Model.software_component import SoftwareComponent


class Host:
    """
    Represents attacked host given on the input.
    """

    def __init__(self, ip, domains, contacts, os_cpe, antivirus_cpe, cms_cpe,
                 cve_count, event_count):
        self.ip = ip
        self.domains = domains
        self.contacts = contacts
        self.os_component = SoftwareComponent("os_component", os_cpe) \
            if os_cpe is not None else None
        self.antivirus_component = SoftwareComponent("antivirus_component",
                                                     antivirus_cpe) \
            if antivirus_cpe is not None else None
        self.cve_count = cve_count
        self.event_count = event_count
        self.cms = SoftwareComponent("cms_component", cms_cpe) \
            if cms_cpe is not None else None
        self.network_services = []

    def __str__(self):
        return f"IP: {self.ip}\n" \
               f"DOMAIN(s): {self.domains}\n" \
               f"OS: {self.os_component}\n" \
               f"ANTIVIRUS: {self.antivirus_component}\n" \
               f"CMS: {self.cms}\n" \
               f"CVE: {self.cve_count}\n" \
               f"EVENTS: {self.event_count}\n" \
               f"NS: {[ns.__str__() for ns in self.network_services]}"


class HostWithScore(Host):
    """
    Represents nearby hosts evaluated with score and distance.
    """

    def __init__(self, ip, domains, contacts, os_cpe, antivirus_cpe, cms_cpe,
                 cve_count, event_count, distance, path_type):
        super().__init__(ip, domains, contacts, os_cpe, antivirus_cpe, cms_cpe,
                         cve_count, event_count)
        self.distance = distance
        self.path_type = path_type
        self.warnings = []
        self.risk = None

    def add_warning_message(self, warning_message):
        """
        Adds warning message to the list of warnings of a host.
        :param warning_message: WarningMessage object for adding
        :return: None
        """
        self.warnings.append(warning_message)

    def to_json(self):
        domains = \
            [] if self.domains[0] == 'Domain name not found' else self.domains
        return {
            "ip": str(self.ip),
            "domains": domains,
            "risk": round(self.risk, 4)
        }

    def to_json_verbose(self):
        json = self.to_json()
        json["os"] = self.os_component
        json["antivirus"] = self.antivirus_component
        json["cms"] = self.cms
        json["cve_count"] = self.cve_count
        json["security_event_count"] = self.event_count
        json["network_services"] = self.network_services
        json["distance"] = self.distance
        json["path_type"] = self.path_type
        json["path_type"] = self.path_type
        json["warnings"] = self.warnings
        return json

    def to_csv(self, verbose):
        domains = '' if self.domains[0] \
                        == 'Domain name not found' else ','.join(self.domains)
        csv = f"{self.ip};{domains};{round(self.risk)}"

        if verbose:
            csv += f";{','.join(str(warning) for warning in self.warnings)}"

        return csv
