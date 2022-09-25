from recommender.comparators.cpe_comparator import CpeComparator


class OsComparator(CpeComparator):
    """
    Operating system comparator
    """

    def calc_partial_similarity(self, host):
        """
        Calculates partial similarity of operating systems running on
        given hosts.
        :param host: Host object (host to be compared with reference host)
        :return: Partial similarity of OS components.
        """

        partial_similarity, critical = self._compare_sw_components(
            self._reference_host.os_component, host.os_component)

        if critical:
            self._add_warning_message(host, "Similar OS between hosts.",
                                      partial_similarity)

        return partial_similarity
