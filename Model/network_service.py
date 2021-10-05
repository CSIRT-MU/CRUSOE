class NetworkService:
    """
    Represents network service running on a host.
    """
    def __init__(self, port, protocol, service):
        self.port = port
        self.protocol = protocol
        self.service = service
