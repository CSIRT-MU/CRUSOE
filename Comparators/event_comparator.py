from Comparators.cumulative_comparator import CumulativeSimilarityComparator


class EventComparator(CumulativeSimilarityComparator):
    def __init__(self, config, total_event_count):
        super().__init__(config)
        self.total_event_count = total_event_count

    def calc_partial_similarity(self, host):
        """
        Calculates cumulative similarity of number of events on hosts
        :param host1: Compared host
        :return: Cumulative partial similarity
        """
        return self._calculate_cumulative_similarity(self.reference_host.event_count,
                                                     host.event_count,
                                                     self.total_event_count)
