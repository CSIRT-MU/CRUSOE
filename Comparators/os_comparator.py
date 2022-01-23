from Comparators.cpe_comparator import CpeComparator


class OsComparator(CpeComparator):

    def __init__(self, config):
        super().__init__(config)

    def calc_partial_similarity(self, host):
        """
        Calculates partial similarity by comparing operating systems running on
        given hosts.
        :param host: Host object (host to be compared with reference host)
        :return: Partial similarity of OS.
        """
        return self._compare_sw_components(self.reference_host.os_component,
                                           host.os_component)
