from recommender.comparators import *
from recommender.model.path_type import PathType


class RiskCalculator:
    """
    Calculates risk scores between attacked host and host found in close
    proximity.
    """

    def __init__(self, db_client, config):
        self.__db_client = db_client
        self.__config = config
        self.__comparators = []

        self.__path_coefficients = {
            PathType.Subnet: self.__config["path"]["subnet"],
            PathType.Organization: self.__config["path"]["organization_unit"],
            PathType.Contact: self.__config["path"]["contact"],
        }

        self.__available_comparators = [
            "os",
            "antivirus",
            "cms",
            "cve_cumulative",
            "event_cumulative",
            "net_service"
        ]

        self.__initialize_comparators()

    def calculate_risk_scores(self, attacked_host, compared_hosts):
        """
        Calculates and sets risk score for every host in compared_hosts list.
        :param attacked_host: Attacked host to which hosts are compared to
        :param compared_hosts: List of hosts which risk should be calculated
        :return: None
        """
        self.__set_reference_host(attacked_host)

        for host in compared_hosts:
            host.risk = self.__calculate_risk_score(host)

    def calculate_similarities(self, host1, host2):
        """
        Calculates similarity of two hosts. Returns result similarity and dictionary of all partial similarities.
        :param host1: First host
        :param host2: Second host
        :return: Similarity and dictionary of partial similarities
        """
        self.__set_reference_host(host1)

        similarity = 1
        partial_similarity_vector = dict()

        for comparator in self.__comparators:
            partial_similarity = comparator.calc_partial_similarity(host2)
            partial_similarity_vector[comparator.get_name()] = partial_similarity
            similarity *= partial_similarity

        return similarity, partial_similarity_vector

    def __initialize_comparators(self):
        """
        Initialize comparators that should be applied by config.
        :return: None
        """
        self.__comparators = []

        for comparator in self.__available_comparators:
            if self.__config["comparators"][comparator]["apply"]:
                config = self.__config["comparators"][comparator]
                comp = None
                match comparator:
                    case "os":
                        comp = OsComparator(config)
                    case "antivirus":
                        comp = AntivirusComparator(config)
                    case "cms":
                        comp = CmsComparator(config)
                    case "cve_cumulative":
                        comp = CveComparator(
                            config, self.__db_client.get_total_cve_count())
                    case "event_cumulative":
                        comp = EventComparator(
                            config, self.__db_client.get_total_event_count())
                    case "net_service":
                        comp = NetServicesComparator(config)

                if comp is not None:
                    self.__comparators.append(comp)

    def __set_reference_host(self, attacked_host):
        """
        Sets reference host to every comparator in the comparator list.
        :return: None
        """
        for comparator in self.__comparators:
            comparator.set_reference_host(attacked_host)

    def __calculate_risk_score(self, compared_host):
        """
        Compares attacked host with given host by applying the list
        of comparators. Result similarity is divided by distance between hosts
        and multiplied by path coefficient.
        :param compared_host: Host to be compared with attacked host
        :return: Risk score between attacked host and compared host
        Sets reference host to every comparator in the comparator list
        """

        # Default similarity is 1
        similarity = 1

        # Multiply result similarity by partial similarities obtained
        # by applying list of comparators on compared host
        for comparator in self.__comparators:
            similarity *= comparator.calc_partial_similarity(compared_host)

        # Multiply similarity by path type coefficient(s)
        if self.__config["path"]["apply"]:
            for path_type in compared_host.path_types:
                similarity *= self.__path_coefficients[path_type]

        # Divide similarity by distance
        return similarity / compared_host.distance
