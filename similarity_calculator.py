from Model.path_type import PathType


class SimilarityCalculator:

    def __init__(self, config, attacked_host, comparator_list):
        self.config = config
        self.attacked_host = attacked_host
        self.comparator_list = comparator_list

        self.path_coefficients = {
            PathType.Subnet: self.config["subnet"],
            PathType.Organization: self.config["organization"],
            PathType.Contact: self.config["contact"],
        }

    def calculate_risk_scores(self, close_hosts):
        """

        :param close_hosts:
        :return:
        """

        for host in close_hosts:
            host.risk = self.calculate_risk_score(host)

    def calculate_risk_score(self, close_host):
        """

        :param close_host:
        :return:
        """
        similarity = 1

        # Multiply result similarity by partial similarities obtained
        # by applying comparators on all hosts
        for comparator in self.comparator_list:
            comparator.set_reference_host(self.attacked_host)
            similarity *= comparator.calc_partial_similarity(close_host)

        # Multiply similarity by path type coefficient
        similarity *= self.path_coefficients[close_host.path_type]

        return similarity / close_host.distance
