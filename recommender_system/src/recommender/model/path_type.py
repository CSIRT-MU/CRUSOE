from enum import Enum


class PathType(Enum):
    """
    Type of path from attacked host to nearby hosts.
    """
    Subnet = 1
    Contact = 2
    Organization = 3

    def to_json(self):
        return self.name

    def __str__(self):
        return self.name
