class NetworkService:
    """
    Represents network service running on a host.
    """
    def __init__(self, port, protocol, service):
        self.port = port
        self.protocol = protocol
        self.service = service

    def __str__(self):
        return f"{self.service}:{self.protocol}:{self.port}"

    def to_json(self):
        return {
            "service": self.service,
            "port": self.port,
            "protocol": self.protocol
        }
