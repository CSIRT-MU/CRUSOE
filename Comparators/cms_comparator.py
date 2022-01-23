from Comparators.cpe_comparator import CpeComparator


class CmsComparator(CpeComparator):

    def __init__(self, config):
        super().__init__(config)
        self.ref_host_open_ports = None

    def set_reference_host(self, host):
        """
        Sets reference host for comparing and checks if it has opened
        HTTP(s) ports.
        :param host: Host object
        :return: None
        """
        self.reference_host = host
        self.ref_host_open_ports = self.__check_http_ports(host)

    def calc_partial_similarity(self, host):
        """
        Calculates partial similarity by comparing content management systems
        (CMS) running on compared hosts. Open HTTP(S) ports might be required
        for this compare, depending on config file.
        :param host: Host object (host to be compared with reference host)
        :return: Partial similarity of cms software
        """
        if self.config["require_open_http"]:
            # Check if both hosts have opened HTTP(S) ports
            if self.__check_http_ports(host) != self.ref_host_open_ports:
                return self.config["diff_value"]
            # Both hosts have closed ports
            if not self.ref_host_open_ports:
                return 1

        return self._compare_sw_components(self.reference_host.cms, host.cms)

    @staticmethod
    def __check_http_ports(host):
        """
        Checks whether given host has opened HTTP or HTTPS ports.
        :return: Bool
        """
        for net_service in host.network_services:
            if net_service.protocol == "TCP" and \
                    (net_service.port == 80 or net_service == 443):
                return True
        return False
