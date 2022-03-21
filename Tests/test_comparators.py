import unittest
from Comparators import *
from Model.host import HostWithScore
from Model.network_service import NetworkService


class TestComparators(unittest.TestCase):

    def __init__(self, methodName):
        super().__init__(methodName)

        # Initialize test data
        self.test_hosts = [
            HostWithScore("123.123.123.123", ["test.cz"], ["test@email.cz"], "microsoft:windows:10", None, "apache:http_server:2.4.10", 54, 0, 0, 0),
            HostWithScore("123.123.123.123", ["test.cz"], ["test@email.cz"], "apple:macOS:monterey", "*:*:*", "apache:http_server:2.4.18", 23, 0, 0, 0),
            HostWithScore("123.123.123.123", ["test.cz"], ["test@email.cz"], "microsoft:windows:xp", "eset:nod32:1.2", "microsoft:iis:8.5", 120, 0, 0, 0),
            HostWithScore("123.123.123.123", ["test.cz"], ["test@email.cz"], "apple:ios:12.1", "eset:*:*", "apache:http_server:*", 0, 0, 0, 0),
            HostWithScore("123.123.123.123", ["test.cz"], ["test@email.cz"], "google:android:8.1", "avast:free_antivirus:4.2", "nginx:n:12", 142, 0, 0, 0),
            HostWithScore("123.123.123.123", ["test.cz"], ["test@email.cz"], "microsoft:windows:10", "eset:nod32:1.5", "nginx:nginx:1.5.8", 90, 0, 0, 0),
            HostWithScore("123.123.123.123", ["test.cz"], ["test@email.cz"], "google:*:*", None, None, 1, 0, 0, 0),
            HostWithScore("123.123.123.123", ["test.cz"], ["test@email.cz"], "*:*:*", "avast:antivirus:4.2", "nginx:nginx:1.12.1", 22, 0, 0, 0)
        ]

    def test_os_comparator(self):

        test_config = {
            "vendor": 0.125,
            "product": 0.75,
            "version": 0.125,
            "diff_value": 0.1,
            "critical_bound": 0.875
        }

        comparator = OsComparator(test_config)

        comparator.set_reference_host(self.test_hosts[0])

        warn_count = len(self.test_hosts[2].warnings)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[2]),
            0.875)
        self.assertEqual(warn_count, len(self.test_hosts[2].warnings))

        warn_count = len(self.test_hosts[5].warnings)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[5]),
            1)
        self.assertEqual(warn_count + 1, len(self.test_hosts[5].warnings))

        warn_count = len(self.test_hosts[1].warnings)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[1]),
            0.1)
        self.assertEqual(warn_count, len(self.test_hosts[1].warnings))

        warn_count = len(self.test_hosts[7].warnings)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[7]),
            1)
        self.assertEqual(warn_count + 1, len(self.test_hosts[7].warnings))

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
            "diff_value": 0.3,
            "critical_bound": 0.7
        }

        comparator = AntivirusComparator(test_config)

        comparator.set_reference_host(self.test_hosts[2])

        warn_count = len(self.test_hosts[3].warnings)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[3]),
            1)
        self.assertEqual(warn_count + 1, len(self.test_hosts[3].warnings))

        warn_count = len(self.test_hosts[0].warnings)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[0]),
            0.3)
        self.assertEqual(warn_count, len(self.test_hosts[0].warnings))

        warn_count = len(self.test_hosts[5].warnings)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[5]),
            0.75)
        self.assertEqual(warn_count + 1, len(self.test_hosts[5].warnings))

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

    def test_cms_comparator(self):
        test_config = {
            "vendor": 0.5,
            "product": 0.25,
            "version": 0.25,
            "diff_value": 0.8,
            "critical_bound": 0.7,
            "require_open_http": False
        }

        comparator = CmsComparator(test_config)

        # Without http required
        comparator.set_reference_host(self.test_hosts[0])

        warn_count = len(self.test_hosts[1].warnings)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[1]), 0.75)
        self.assertEqual(warn_count + 1, len(self.test_hosts[1].warnings))

        warn_count = len(self.test_hosts[3].warnings)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[3]), 1)
        self.assertEqual(warn_count + 1, len(self.test_hosts[3].warnings))

        warn_count = len(self.test_hosts[2].warnings)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[2]), 0.8)
        self.assertEqual(warn_count, len(self.test_hosts[2].warnings))

        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[6]), 0.8)

        comparator.set_reference_host(self.test_hosts[5])

        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[7]), 0.75)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[3]), 0.8)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[6]), 0.8)
        warn_count = len(self.test_hosts[4].warnings)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[4]), 0.5)
        self.assertEqual(warn_count, len(self.test_hosts[4].warnings))

        # With http required
        test_config["require_open_http"] = True
        http = NetworkService(80, "TCP", "http")
        https = NetworkService(443, "TCP", "https")
        self.test_hosts[0].network_services = [http]
        self.test_hosts[2].network_services = [https]
        self.test_hosts[3].network_services = [http]
        self.test_hosts[7].network_services = [https]

        comparator.set_reference_host(self.test_hosts[0])

        warn_count = len(self.test_hosts[1].warnings)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[1]), 0.8)
        self.assertEqual(warn_count, len(self.test_hosts[1].warnings))

        warn_count = len(self.test_hosts[3].warnings)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[3]), 1)
        self.assertEqual(warn_count + 1, len(self.test_hosts[3].warnings))

        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[2]), 0.8)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[6]), 0.8)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[7]), 0.8)

        comparator.set_reference_host(self.test_hosts[5])

        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[7]), 0.8)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[3]), 0.8)

        warn_count = len(self.test_hosts[6].warnings)
        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[6]), 1)
        self.assertEqual(warn_count, len(self.test_hosts[6].warnings))

        self.assertEqual(comparator.calc_partial_similarity(
            self.test_hosts[4]), 1)

    def test_net_service_comparator(self):
        test_config = {
            "diff_value": 0.3,
            "critical_bound": 0.7
        }

        comparator = NetServicesComparator(test_config)

        self.test_hosts[0].network_services = [
            NetworkService(80, "TCP", "http"),
            NetworkService(20, "TCP", "ftp"),
            NetworkService(53, "UDP", "dns"),
            NetworkService(25, "TCP", "smtp"),
        ]

        self.test_hosts[1].network_services = [
            NetworkService(80, "TCP", "http"),
            NetworkService(20, "TCP", "ftp"),
            NetworkService(53, "TCP", "dns"),
            NetworkService(194, "TCP", "irc")
        ]

        comparator.set_reference_host(self.test_hosts[0])

        self.assertAlmostEqual(comparator.calc_partial_similarity(
            self.test_hosts[1]), 1 / 3)

        self.test_hosts[2].network_services = [
            NetworkService(80, "TCP", "http"),
            NetworkService(20, "TCP", "ftp"),
            NetworkService(53, "UDP", "dns"),
            NetworkService(25, "TCP", "smtp"),
        ]

        self.assertAlmostEqual(comparator.calc_partial_similarity(
            self.test_hosts[2]), 1)

        self.test_hosts[3].network_services = []

        self.assertAlmostEqual(comparator.calc_partial_similarity(
            self.test_hosts[3]), test_config["diff_value"])

        comparator.set_reference_host(self.test_hosts[3])

        self.assertAlmostEqual(comparator.calc_partial_similarity(
            self.test_hosts[3]), 1)

        self.test_hosts[0].network_services = [
            NetworkService(80, "TCP", "http"),
            NetworkService(20, "TCP", "ftp")
        ]

        comparator.set_reference_host(self.test_hosts[0])

        self.test_hosts[4].network_services = [
            NetworkService(80, "TCP", "http"),
            NetworkService(20, "TCP", "ftp")
        ]

        warning_count = len(self.test_hosts[4].warnings)

        self.assertAlmostEqual(comparator.calc_partial_similarity(
            self.test_hosts[4]), 1)

        self.assertEqual(warning_count + 1, len(self.test_hosts[4].warnings))

    def test_cve_comparator(self):
        test_config = {
            "diff_value": 0.3,
            "critical_bound": 0.7
        }

        total_cve = 120
        comparator = CveComparator(test_config, total_cve)

        comparator.set_reference_host(self.test_hosts[0])

        self.assertAlmostEqual(comparator.calc_partial_similarity(
            self.test_hosts[1]), )

    def test_event_comparator(self):

        test_config = {
            "diff_value": 0.3,
            "critical_bound": 0.7
        }

        total_events = 154


if __name__ == '__main__':
    unittest.main()
