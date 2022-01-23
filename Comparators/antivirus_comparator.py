from Comparators.cpe_comparator import CpeComparator


class AntivirusComparator(CpeComparator):

    def __init__(self, config):
        super().__init__(config)

    def calc_partial_similarity(self, host):
        """
        Calculates partial similarity of antivirus software running on
        compared hosts.
        :param host: Host object (host to be compared with reference host)
        :return: Partial similarity of antivirus sw.
        """
        return self._compare_sw_components(
            self.reference_host.antivirus_component, host.antivirus_component)
