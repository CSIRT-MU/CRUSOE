from Comparators.cpe_comparator import CpeComparator


class AntivirusComparator(CpeComparator):

    def __init__(self, config):
        super().__init__(config)

    def calc_partial_similarity(self, host):
        """

        :param host:
        :return:
        """

        if self.reference_host.antivirus_component is None \
                and host.antivirus_component is None:
            return 1

        if self.reference_host.antivirus_component is None \
                or host.antivirus_component is None:
            return self.config["diff_value"]

        compare_result = self._compare_sw_components(self.reference_host.
                                                     antivirus_component,
                                                     host.antivirus_component,
                                                     self.weights)

        # Zero similarity -> use configured value of similarity (can be zero)
        if compare_result == 0:
            return self.config["diff_value"]
        return compare_result
