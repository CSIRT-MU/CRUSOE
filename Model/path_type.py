from enum import Enum


class PathType(Enum):
    Subnet = 1
    Contact = 2
    Organization = 3

    def to_json(self):
        return self.name
