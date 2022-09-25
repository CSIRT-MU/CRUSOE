from abc import ABC
from statistics import mean

from recommender.comparators.base_comparator import BaseComparator


class CpeComparator(BaseComparator, ABC):
    """
    Abstract comparator for comparing based on cpe strings
    """
    def __init__(self, config):
        super().__init__(config)
        self.__weights = [
            config["vendor"],
            config["product"],
            config["version"]
        ]

    def _compare_sw_components(self, sw1, sw2):
        """
        Compares two software components and returns partial similarity.
        :param sw1: First SW component
        :param sw2: Second SW component
        :return: Partial similarity (float in <0,1>) between sw1 and sw2
        and information if critical bound was reached
        """
        # Both hosts do not have this SW component
        if sw1 is None and sw2 is None:
            return 1, False

        # Only one of the hosts has this SW component, use predefined diff
        # value
        if sw1 is None or sw2 is None:
            return self._config["diff_value"], False

        compare_result = self.compare_cpe(sw1.cpe_list, sw2.cpe_list)

        # Zero similarity -> use configured diff value
        if compare_result == 0:
            return self._config["diff_value"], False
        return compare_result, self._check_critical_bound(compare_result)

    def compare_cpe(self, list1, list2):
        """
        Compares two cpe string in form of list of CPE parts and evaluates
        similarity with list of weights for each part.
        :param list1: First CPE list
        :param list2: Second CPE list
        :return: Result similarity (float in range <0,1>)
        """
        result_similarity = 0

        # Take the shorter CPE, CPE might miss some part(s) (e.g. error)
        for i in range(min(len(list1), len(list2))):
            if CpeComparator._compare_cpe_parts(list1[i], list2[i]):
                # Add cpe part weight to result when parts match
                result_similarity += self.__weights[i]
            else:
                break

        return result_similarity

    @staticmethod
    def _compare_cpe_parts(part1, part2):
        """
        Compares two CPE elements. Elements are the same, if they are equal or
        one of them is * (ANY).
        :param part1: First CPE string part
        :param part2: Second CPE string part
        :return: True if CPE parts are same, False otherwise
        """
        return part1 == part2 or part1 == "*" or part2 == "*"
