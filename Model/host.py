class Host:
    """
    Represents one host in the network.
    """
    def __init__(self, ip, domains, os_cpe):
        self.ip = ip
        self.domains = domains
        self.os_cpe = os_cpe
        self.software_components = []
        self.network_services = []


class HostWithScore(Host):
    """
    Represents nearby hosts evaluated with score and distance
    """
    def __init__(self, ip, domains, os_cpe):
        Host.__init__(self, ip, domains, os_cpe)
        self.risk_score = None
        self.distance = None

