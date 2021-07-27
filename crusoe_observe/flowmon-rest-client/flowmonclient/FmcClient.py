from .resources.fmc.Profiles import Profiles
from .resources.fmc.Analysis import Analysis
from .AbstractClient import AbstractClient


class FmcClient(AbstractClient):
    def __init__(self, *args, **kwargs):
        """ Monitoring Center client """
        super().__init__(*args, **kwargs)
        self.endpoint_base += "/fmc"

        # Resources
        self.profiles = Profiles(self)
        self.analysis = Analysis(self)
