from recommender.comparators.cpe_comparator import CpeComparator


class CmsComparator(CpeComparator):
    """
    Content management system comparator.
    """

    def __init__(self, config):
        super().__init__(config)
        self.__ref_host_open_ports = None

    def set_reference_host(self, host):
        """
        Sets reference host for comparing and checks if it has opened
        HTTP(s) ports.
        :param host: Host object
        :return: None
        """
        self._reference_host = host
        self.__ref_host_open_ports = self.__check_http_ports(host)

    def calc_partial_similarity(self, host):
        """
        Calculates partial similarity by comparing content management systems
        (CMS) running on compared hosts. Open HTTP(S) ports might be required
        for this comparison, depending on the config file.
        :param host: Host object (host to be compared with reference host)
        :return: Partial similarity of cms software
        """
        if self._config["require_open_ports"]:
            # Check if both hosts have opened HTTP(S) ports
            if self.__check_http_ports(host) != self.__ref_host_open_ports:
                return self._config["diff_value"]
            # Both hosts have closed ports
            if not self.__ref_host_open_ports:
                return 1

        # Calculate partial similarity
        partial_similarity, critical = self.compare_sw_components(
            self._reference_host.cms, host.cms)

        if critical:
            message = "Similar CMS between hosts"
            # Add information about open http(s) ports to the output
            if self._config["require_open_ports"]:
                message += ", both hosts have open HTTP(S) ports"

            self._add_warning_message(host, message, partial_similarity)

        return partial_similarity

    @staticmethod
    def __check_http_ports(host):
        """
        Checks whether given host has opened HTTP or HTTPS ports.
        :return: Bool
        """
        for net_service in host.network_services:
            if net_service.protocol == "TCP" and \
                    (net_service.port == 80 or net_service.port == 443):
                return True
        return False
