from Comparators.cpe_comparator import CpeComparator


class CmsComparator(CpeComparator):

    def __init__(self, config):
        super().__init__(config)

    def calc_partial_similarity(self, host):
        """

        :param host:
        :return:
        """


    def check_net_ports(self):
        """
        HTTP: 80
        HTTPS: 443
        :return:
        """

