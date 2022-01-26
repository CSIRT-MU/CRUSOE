import unittest
from Comparators import *
from Model.host import Host


class TestComparators(unittest.TestCase):

    def __init__(self, methodName):
        super().__init__(methodName)

        # Initialize test
        self.test_hosts = [
            Host("123.123.123.123",
                 "test.cz", "microsoft:windows:10", None, 0, 0),
            Host("123.123.123.123",
                 "test.cz", "apple:macOS:monterey", "*:*:*", 0, 0),
            Host("123.123.123.123",
                 "test.cz", "microsoft:windows:xp", "eset:nod32:1.2", 0, 0),
            Host("123.123.123.123",
                 "test.cz", "apple:ios:12.1", "eset:*:*", 0, 0),
            Host("123.123.123.123",
                 "test.cz", "google:android:8.1", "avast:free_antivirus:4.2",
                 0, 0),
            Host("123.123.123.123",
                 "test.cz", "microsoft:windows:10", "eset:nod32:1.5", 0, 0),
            Host("123.123.123.123",
                 "test.cz", "google:*:*", None, 0, 0),
            Host("123.123.123.123",
                 "test.cz", "*:*:*", "avast:antivirus:4.2", 0, 0)
        ]

    def test_os_comparator(self):

        test_config = {
            "vendor": 0.125,
            "product": 0.75,
            "version": 0.125,
            "diff_value": 0.1
        }

        comparator = OsComparator(test_config)

        comparator.set_reference_host(self.test_hosts[0])

        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[2]),
            0.875)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[5]),
            1)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[1]),
            0.1)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[7]),
            1)

        comparator.set_reference_host(self.test_hosts[1])

        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[3]),
            0.125)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[5]),
            0.1)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[7]),
            1)

        comparator.set_reference_host(self.test_hosts[4])

        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[3]),
            0.1)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[5]),
            0.1)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[6]),
            1)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[7]),
            1)

    def test_antivirus_comparator(self):

        test_config = {
            "vendor": 0.5,
            "product": 0.25,
            "version": 0.25,
            "diff_value": 0.3
        }

        comparator = AntivirusComparator(test_config)

        comparator.set_reference_host(self.test_hosts[2])

        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[3]),
            1)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[0]),
            0.3)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[5]),
            0.75)

        comparator.set_reference_host(self.test_hosts[4])

        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[7]),
            0.5)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[2]),
            0.3)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[1]),
            1)

        comparator.set_reference_host(self.test_hosts[0])
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[6]),
            1)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[2]),
            0.3)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[1]),
            0.3)

    def test_cve_comparator(self):

        test_config = {
            "vendor": 0.5,
            "product": 0.25,
            "version": 0.25,
            "diff_value": 0.3
        }

    def test_event_comparator(self):

        test_config = {
            "vendor": 0.5,
            "product": 0.25,
            "version": 0.25,
            "diff_value": 0.3
        }


if __name__ == '__main__':
    unittest.main()
