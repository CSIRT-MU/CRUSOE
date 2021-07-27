from .AbstractClient import AbstractClient
from .resources.ads.Events import Events
from .resources.ads.Methods import Methods
from .resources.ads.Perspectives import Perspectives
from .resources.ads.FalsePositives import FalsePositives
from .resources.ads.Filters import Filters


class AdsClient(AbstractClient):
    def __init__(self, *args, **kwargs):
        """ Anomaly Detection System client """
        super().__init__(*args, **kwargs)
        self.endpoint_base += "/ads"

        # Resources
        self.events = Events(self)
        self.methods = Methods(self)
        self.perspectives = Perspectives(self)
        self.false_positives = FalsePositives(self)
        self.filters = Filters(self)
