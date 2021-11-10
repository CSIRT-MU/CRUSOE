from Comparators.cpe_comparator import CpeComparator


class OsComparator(CpeComparator):

    def __init__(self, config):
        super().__init__(config)
        self.weights = [
            config["os_vendor"],
            config["os_product"],
            config["os_version"]
        ]

    def calc_partial_similarity(self, host):
        """
        Compares OS of given host with OS of reference host.
        :param host: Compared host
        :return: Partial similarity of OS.
        """
        return self._compare_sw_components(self.reference_host.os_component,
                                           host.os_component,
                                           self.weights)
