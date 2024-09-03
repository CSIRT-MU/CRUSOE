"""
Module config_decomposition_test.py tests functionality which determines all configurations
for a mission.
"""

import json
import unittest
import pkg_resources
from neo4jclient.MissionAndComponentClient import MissionAndComponentClient
from neo4jclient.RESTClient import RESTClient
from crusoe_decide.process import get_possible_configurations


CONSTRAINT_FILE = pkg_resources.resource_filename(__name__, 'test_data/constraint.json')
MISSION_FILE = pkg_resources.resource_filename(__name__, 'test_data/missions.json')


class DecompositionTestCase(unittest.TestCase):
    """
    Class for testing functionality of mission decomposition process.
    """
    def test_example_cases(self):
        """
        Tests example of mission file. It finds combinations of components (configurations)
        for which the computation in another parts of analytical process will continue.
        For example: for A and (B or C) returns two possible combinations - A and B,
        A and C in the form [{'A', 'B'}, {'A', 'C}]. For representation of components,
        IDs are used.

        :return:
        """
        mission_client = MissionAndComponentClient(password="ne04jcrus03")
        rest_client = RESTClient(password="ne04jcrus03")

        with open(MISSION_FILE, "r") as json_file:
            data = json.load(json_file)
        rest_client.create_missions_and_components_string(str(data))
        self.assertEqual({'Acquisition': [{20, 22}, {20, 23}, {21, 22}, {21, 23}, {24, 25, 26, 20},
                                          {24, 25, 26, 21}],
                          'Diagnostics': [{24, 25, 26, 30}, {27, 22}, {28, 22}, {29, 22}, {27, 23},
                                          {28, 23}, {29, 23}]},
                         get_possible_configurations(
                             mission_client, [{'mission': {'name': 'Acquisition'}},
                                              {'mission': {'name': 'Diagnostics'}}]))

        with open(CONSTRAINT_FILE, "r") as json_file:
            data = json.load(json_file)
        rest_client.create_missions_and_components_string(str(data))
        self.assertEqual({'Web mission': [{20, 21}, {20, 22}]},
                         get_possible_configurations(
                             mission_client, [{'mission': {'name': 'Web mission'}}]))
