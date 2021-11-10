class SimilarityCalculator:

    def __init__(self, config, attacked_host, comparator_list):
        self.config = config
        self.attacked_host = attacked_host
        self.comparator_list = comparator_list

    def calculate_similarities(self, close_hosts):
        """

        :param close_hosts:
        :return:
        """

        for host in close_hosts:
            host.risk = self.calculate_similarity(host)

    def calculate_similarity(self, close_host):
        """

        :param close_host:
        :return:
        """
        similarity = 1

        # Apply comparators on given hosts to get partial similarities
        for comparator in self.comparator_list:
            comparator.set_reference_host(self.attacked_host)
            similarity *= comparator.calc_partial_similarity(close_host)

        return similarity / close_host.distance
