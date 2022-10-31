from abc import ABC

from recommender.comparators.base_comparator import BaseComparator


class CumulativeSimilarityComparator(BaseComparator, ABC):
    """
    Abstract comparator for comparing based on the cumulative history of hosts.
    """

    def _calculate_cumulative_similarity(self, n1, n2, total):
        """
        Calculates cumulative partial similarity of some attribute, e.g.
        number of CVEs.
        :param n1: Number of occurrences on the first host
        :param n2: Number of occurrences on the second host
        :param total: Total number of occurrences in the network
        :return: Cumulative partial similarity
        """

        avg = (n1 + n2) / 2.0

        # Check zero values to avoid dividing by zero / returning zero
        if avg == 0:
            return 1.0 / total, False

        if total == 0:
            return 1, False

        result = avg / total

        return result, self._check_critical_bound(result)
