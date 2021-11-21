class BaseComparator:
    """
    Abstract class serving as a base class for all comparator objects.
    """
    def __init__(self, config):
        self.config = config
        self.reference_host = None

    def set_reference_host(self, host):
        """
        Sets reference host for comparing.
        :param host: Host object
        :return: None
        """
        self.reference_host = host

    def calc_partial_similarity(self, host):
        """
        Calculates partial similarity defined by comparator. Must be overridden
        in child classes, otherwise default similarity is returned (1).
        :param host: Host object (host to be compared with reference host)
        :return: Partial similarity (number in <0,1>)
        """
        return 1
