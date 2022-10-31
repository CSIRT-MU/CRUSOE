from abc import ABC, abstractmethod
from recommender.model.warning_message import WarningMessage


class BaseComparator(ABC):
    """
    Abstract class serving as a base class for all comparator objects.
    """

    def __init__(self, config):
        self._config = config
        self._reference_host = None

    @abstractmethod
    def calc_partial_similarity(self, host):
        """
        Calculates partial similarity defined by this comparator.
        :param host: Host object (host to be compared with reference host)
        :return: Partial similarity (number in interval <0,1>)
        """
        pass

    def _check_critical_bound(self, partial_similarity):
        """
        Checks if the calculated partial similarity is higher than the value
        predefined in the config for this comparator.
        :param partial_similarity: Partial similarity in <0,1>
        :return: True if higher than the critical bound
        """
        return partial_similarity > self._config["critical_bound"]

    @staticmethod
    def _add_warning_message(host, message, partial_similarity):
        """
        Adds a warning message to a host.
        :param host: Host to add a warning message
        :param message: String warning, what is causing similarity
        :param partial_similarity: Partial similarity in <0,1>
        :return: None
        """
        warning = WarningMessage(message, partial_similarity)
        host.add_warning_message(warning)

    def set_reference_host(self, host):
        """
        Sets reference host for comparing.
        :param host: Host object
        :return: None
        """
        self._reference_host = host
