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

        if self.reference_host.os_component is None \
                and host.os_component is None:
            return 1

        if self.reference_host.os_component is None \
                or host.os_component is None:
            return self.config["diff_value"]

        compare_result = self._compare_sw_components(self.reference_host.
                                                     os_component,
                                                     host.os_component,
                                                     self.weights)

        # Zero similarity -> use configured value of similarity (can be zero)
        if compare_result == 0:
            return self.config["diff_value"]
        return compare_result
