from Comparators.base_comparator import BaseComparator


class NetServicesComparator(BaseComparator):

    def __init__(self, config):
        super().__init__(config)

    def set_reference_host(self, host):
        """
        Overrides base set_reference_host, adds ordering of host's net
        services for comparing.
        :param host: Host object
        :return: None
        """
        self._sort_net_services(host)
        self.reference_host = host

    def calc_partial_similarity(self, host):
        """
        Calculates partial similarity by summing number of services running on
        both hosts divided by total number of distinct services found on these
        two host. When similarity is zero (no similar net services),
        predefined value from configuration is returned.
        :param host: Host object (host to be compared with reference host)
        :return: Partial similarity (number in <0,1>)
        """

        # Sort network services on the host
        self._sort_net_services(host)

        i1 = 0
        i2 = 0
        ns1_list = self.reference_host.network_services
        ns2_list = host.network_services

        len1 = len(ns1_list)
        len2 = len(ns2_list)

        if len1 == 0 and len2 == 0:
            return 1

        same_service_count = 0

        while i1 < len1 and i2 < len2:
            if ns1_list[i1].protocol == ns2_list[i2].protocol \
                    and ns1_list[i1].port == ns2_list[i2].port:
                same_service_count += 1
                i1 += 1
                i2 += 1
            elif ns1_list[i1].protocol > ns2_list[i2].protocol \
                    or ns1_list[i1].port > ns2_list[i2].port:
                i2 += 1
            elif ns1_list[i1].protocol < ns2_list[i2].protocol \
                    or ns1_list[i1].port < ns2_list[i2].port:
                i1 += 1

        if same_service_count == 0:
            return self.config["diff_value"]

        return same_service_count / (len1 + len2 - same_service_count)

    @staticmethod
    def _sort_net_services(host):
        """
        Sorts network services by protocol and port.
        :param host: Host that network services list should be sorted.
        :return: None
        """
        host.network_services.sort(key=lambda n: (n.protocol, n.port))
