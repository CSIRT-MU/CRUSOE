from recommender.risk_calculator import RiskCalculator


class Recommender:
    """
    The main recommender class. Uses Neo4j client to find the attacked host
    and hosts in proximity. Then calculates scores and sorts them
    appropriately.
    """

    def __init__(self, config, db_client, logger):
        self.__logger = logger
        self.__db_client = db_client
        self.__config = config

        self.attacked_host = None
        self.host_list = []

    def get_attacked_host_by_ip(self, ip):
        """
        Finds attacked host in the database by its IP address and loads it
        in the attacked_host attribute.
        :param ip: IP address of the attacked host
        :return: None
        :except ValueError - if the given IP doesn't exist in the database.
        """
        self.attacked_host = self.__db_client.get_host_by_ip(ip)

    def get_attacked_host_by_domain(self, domain):
        """
        Finds attacked host in the database by its domain name and loads it
        in attacked_host attribute.

        :param domain: Domain name of the attacked host
        :return: None
        :except ValueError - if the given domain doesn't exist in the database.
        """
        self.attacked_host = self.__db_client.get_host_by_domain(domain)

    def recommend_hosts(self):
        """
        Finds close hosts and calculates risk for them. The attacked host must
        be found before the search (throws ValueError exception otherwise.
        Saves recommended hosts in the host_list attribute.
        :return: None
        """

        if self.attacked_host is None:
            raise ValueError("Attacked host is None.")

        # Start BFS from attacked host IP and find hosts in proximity
        self.host_list = self.__db_client.find_close_hosts(
            self.attacked_host.ip,
            self.__config["max_distance"])

        # Calculate risk scores
        risk_calc = RiskCalculator(self.__db_client, self.__config)

        risk_calc.calculate_risk_scores(self.attacked_host, self.host_list)

        # Sorts list of host by risk of exploiting (descending)
        self.host_list.sort(key=lambda h: h.risk, reverse=True)

    def compare_hosts(self, ip1, ip2, max_distance=4):
        """
        Compares two hosts in the databases and returns a dictionary containing distance between them,
        their similarity and all partial similarities.
        :param ip1: IP address of the first host
        :param ip2: IP address of the second host
        :param max_distance: Maximum distance to consider
        :return: Dictionary with similarity, distance and partial similarities
        """
        host1 = self.__db_client.get_host_by_ip(ip1)
        host2 = self.__db_client.get_host_by_ip(ip2)

        if host1 is None:
            raise ValueError(f"IP address {ip1} was not found in the database.")

        if host2 is None:
            raise ValueError(f"IP address {ip2} was not found in the database.")

        distance = self.__db_client.get_distance(ip1, ip2, max_distance)

        risk_calc = RiskCalculator(self.__db_client, self.__config)

        similarity, partial_sim_vector = risk_calc.calculate_similarities(host1, host2)

        partial_sim_vector["similarity"] = similarity
        partial_sim_vector["distance"] = distance

        return partial_sim_vector
