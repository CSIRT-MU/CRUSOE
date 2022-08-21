from functools import total_ordering


@total_ordering
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

    def __eq__(self, other):
        return self.port == other.port and self.protocol == self.protocol

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return (self.protocol, self.port) < (other.protocol, other.port)

    def to_json(self):
        return {
            "service": self.service,
            "port": self.port,
            "protocol": self.protocol
        }
