from Model.path_type import PathType
from Comparators import *


class SimilarityCalculator:

    def __init__(self, db_connection, config, attacked_host):
        self.db_connection = db_connection
        self.config = config
        self.attacked_host = attacked_host
        self.comparator_list = []

        self.path_coefficients = {
            PathType.Subnet: self.config["path"]["subnet"],
            PathType.Organization: self.config["path"]["organization"],
            PathType.Contact: self.config["path"]["contact"],
        }

        self.available_comparators = [
            "os",
            "antivirus",
            "cms",
            "cve_cumulative",
            "event_cumulative",
            "net_service"
        ]

        self.__initialize_comparators()

    def calculate_risk_scores(self, compared_hosts):
        """
        Calculates and sets risk score for every host in compared_hosts list.
        :param compared_hosts:
        :return:
        """
        self.__set_reference_host()

        for host in compared_hosts:
            host.risk = self.__calculate_risk_score(host)

    def __initialize_comparators(self):
        """
        Initialize comparators that should be applied by config.
        :return: None
        """
        self.comparator_list = []

        for comparator in self.available_comparators:
            if self.config[comparator]["apply"]:
                match comparator:
                    case "os":
                        self.comparator_list.append(
                            OsComparator(self.config["os"]))
                    case "antivirus":
                        self.comparator_list.append(
                            AntivirusComparator(self.config["antivirus"]))
                    case "cms":
                        self.comparator_list.append(
                            CmsComparator(self.config["cms"]))
                    case "cve_cumulative":
                        self.comparator_list.append(CveComparator(
                            self.config["cve_cumulative"],
                            self.db_connection.get_total_cve_count()))
                    case "event_cumulative":
                        self.comparator_list.append(EventComparator(
                            self.config["event_cumulative"],
                            self.db_connection.get_total_event_count()))
                    case "net_service":
                        self.comparator_list.append(
                            NetServicesComparator(self.config["net_service"]))

    def __set_reference_host(self):
        """
        Sets reference host to every comparator in comparator list.
        :return: None
        """
        for comparator in self.comparator_list:
            comparator.set_reference_host(self.attacked_host)

    def __calculate_risk_score(self, compared_host):
        """
        Compares attacked host with given host by applying list of comparators.
        Result similarity is divided by distance between hosts and multiplied
        by path coefficient.
        :param compared_host: Host to be compared with attacked host
        :return: Risk score between attacked host and compared host.
        """

        # Default similarity is 1
        similarity = 1

        # Multiply result similarity by partial similarities obtained
        # by applying list of comparators on compared host
        for comparator in self.comparator_list:
            similarity *= comparator.calc_partial_similarity(compared_host)

        # Multiply similarity by path type coefficient
        if self.config["path"]["apply"]:
            similarity *= self.path_coefficients[compared_host.path_type]

        # Divide similarity by distance
        return similarity / compared_host.distance
