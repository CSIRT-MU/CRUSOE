from Model.warning_message import WarningMessage

class BaseComparator:
    """
    Abstract class serving as a base class for all comparator objects.
    """
    def __init__(self, config):
        self.config = config
        self.reference_host = None

    def _check_critical_bound(self, partial_similarity):
        """

        :param partial_similarity:
        :return:
        """
        return partial_similarity > self.config["critical_bound"]

    @staticmethod
    def _add_warning_message(host, message, partial_similarity):
        """

        :param host:
        :param message:
        :param partial_similarity:
        :return:
        """
        warning = WarningMessage(message, partial_similarity)
        host.add_warning_message(warning)

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
        :return: Partial similarity (number in interval <0,1>)
        """
        return 1
