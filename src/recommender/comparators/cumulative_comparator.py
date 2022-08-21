from abc import ABC
from recommender.comparators.base_comparator import BaseComparator


class CumulativeSimilarityComparator(BaseComparator, ABC):

    def __init__(self, config):
        super().__init__(config)

    def _calculate_cumulative_similarity(self, n1, n2, total):
        """
        Calculates cumulative partial similarity of some attribute, e.g.
        number of CVE.
        :param n1: Number of occurrences on first host
        :param n2: Number of occurrences on second host
        :param total: Total number of occurrences in the network
        :return: Cumulative partial similarity
        """

        # Check zero values to avoid dividing by zero / returning zero
        # similarity, predefined value from config is used in this case
        if n1 == 0 or n2 == 0 or total == 0:
            return self.config["zero_value"], False

        sh1 = n1 / total
        sh2 = n2 / total

        result_similarity = min(sh1, sh2) / max(sh1, sh2)

        return result_similarity, self._check_critical_bound(result_similarity)
