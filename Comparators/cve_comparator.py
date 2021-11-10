from Comparators.cumulative_comparator import CumulativeSimilarityComparator


class CveComparator(CumulativeSimilarityComparator):
    def __init__(self, config, total_cve_count):
        super().__init__(config)
        self.total_cve_count = total_cve_count

    def calc_partial_similarity(self, host):
        """
        Calculates cumulative similarity of number of vulnerabilities (CVE)
        on hosts
        :param host: Compared host
        :return: Cumulative partial similarity
        """

        return self._calculate_cumulative_similarity(self.reference_host.cve_count,
                                                     host.cve_count,
                                                     self.total_cve_count)
