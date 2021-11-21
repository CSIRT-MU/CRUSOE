from Model.software_component import SoftwareComponent


class Host:
    """
    Represents one host in the network.
    """
    def __init__(self, ip, domains, os_cpe, antivirus_cpe, cve_count,
                 event_count):
        self.ip = ip
        self.domains = domains
        self.os_component = SoftwareComponent("os_component", os_cpe) if os_cpe is not None else None
        self.antivirus_component = SoftwareComponent("antivirus_component",
                                                     antivirus_cpe) \
            if antivirus_cpe is not None else None
        self.cve_count = cve_count
        self.event_count = event_count
        self.cms_components = []
        self.network_services = []

    def __str__(self):
        return f"IP: {self.ip}\n" \
               f"DOMAIN(s): {self.domains}\n" \
               f"OS: {':'.join(self.os_component.cpe_list)}\n" \
               f"ANTIVIRUS: {'None' if self.antivirus_component is None else ':'.join(self.antivirus_component.cpe_list)}\n" \
               f"CVE: {self.cve_count}\n"\
               f"EVENTS: {self.event_count}\n" \
               f"CMS: {[sw.__str__() for sw in self.cms_components]}\n" \
               f"NS: {[ns.__str__() for ns in self.network_services]}"


class HostWithScore(Host):
    """
    Represents nearby hosts evaluated with score and distance
    """
    def __init__(self, ip, domains, os_cpe, antivirus_cpe, cve_count,
                 event_count, distance, path_type):
        super().__init__(ip, domains, os_cpe, antivirus_cpe, cve_count,
                         event_count)
        self.distance = distance
        self.path_type = path_type
        self.risk = None
