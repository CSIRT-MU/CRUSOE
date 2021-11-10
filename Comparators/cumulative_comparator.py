from Comparators.comparator_base import BaseComparator


class CumulativeSimilarityComparator(BaseComparator):

    def __init__(self, config):
        super().__init__(config)

    @staticmethod
    def _calculate_cumulative_similarity(n1, n2, total):
        """
        Calculates cumulative partial similarity of some attribute, e.g.
        number of CVE.
        :param n1: Number of occurrences on first host
        :param n2: Number of occurrences on second host
        :param total: Total number of occurrences in the network
        :return: Cumulative partial similarity
        """

        # Check zero values to emmit dividing by zero
        if n1 == 0 or n2 == 0 or total == 0:
            return 1

        sh1 = n1 / total
        sh2 = n2 / total

        return min(sh1, sh2) / max(sh1, sh2)
