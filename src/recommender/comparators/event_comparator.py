from recommender.comparators.cumulative_comparator \
    import CumulativeSimilarityComparator


class EventComparator(CumulativeSimilarityComparator):
    def __init__(self, config, total_event_count):
        super().__init__(config)
        self.total_event_count = total_event_count

    def calc_partial_similarity(self, host):
        """
        Calculates cumulative similarity of number of events on hosts
        :param host: Host object (host to be compared with reference host)
        :return: Cumulative partial similarity
        """

        partial_similarity, critical = self._calculate_cumulative_similarity(
            self._reference_host.event_count,
            host.event_count,
            self.total_event_count)

        if critical:
            message = "High cumulative security incident count"
            self._add_warning_message(host, message, partial_similarity)

        return partial_similarity
