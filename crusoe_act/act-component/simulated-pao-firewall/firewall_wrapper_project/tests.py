from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse


class HealthTest(APITestCase):
    """
    [GET] /firewall/health
    """

    def test_valid_request(self):
        """
        [GET] /firewall/health
        :return: 200, OK
        """
        response = self.client.get(reverse("health_check"))
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_invalid_request(self):
        """
        [GET] /firewall/health1234
        :return: 404, invalid url, not found
        """
        response = self.client.get(path="/firewall/health1234")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_method(self):
        """
        [POST] /firewall/health
        :return: 405, method POST not allowed
        """
        response = self.client.post(reverse("health_check"))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class CapacityTest(APITestCase):
    """
    [GET] /firewall/capacity
    """

    def test_valid_request(self):
        """
        [GET] /firewall/capacity
        :return: 200, OK
        """
        response = self.client.get(reverse("capacity"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_method(self):
        """
        [PUT] /firewall/capacity
        :return: 405, method PUT not allowed
        """
        response = self.client.put(reverse("capacity"))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class BlockedTest(APITestCase):
    """
    [GET] /firewall/blocked
    [POST] /firewall/blocked
    """

    def test_valid_request_get(self):
        """
        [GET] /firewall/blocked
        :return: 200, OK
        """
        response = self.client.get(reverse("blocked"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_valid_request_post(self):
        """
        [POST] /firewall/blocked
        :return: 200, OK
        """
        response = self.client.post(reverse("blocked"), data={
            "ruleIp": "147.251.11.1",
            "rulePort": 7777,
            "ruleReason": "someReason"
        })
        self.assertEqual(response.data['ruleId'], 0)

    def test_invalid_request_post(self):
        """
        [POST] /firewall/blocked
        :return: 400, bad request
        """
        response = self.client.post(reverse("blocked"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_method(self):
        """
        [PUT] /firewall/blocked
        :return: 405, method not allowed
        """
        response = self.client.put(reverse("blocked"))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class BlockedIdTest(APITestCase):
    """
    [GET] /firewall/blocked/{blockedId}
    [DELETE] /firewall/blocked/{blockedId}
    """

    def test_valid_request_get(self):
        """
        [GET] /firewall/blocked/1
        :return: 200, OK
        """
        response = self.client.get(path="/firewall/blocked/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ruleId'], 1)

    def test_valid_request_delete(self):
        """
        [DELETE] /firewall/blocked/1
        :return: 200, OK
        """
        response = self.client.delete(path="/firewall/blocked/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ruleId'], 1)

    def test_invalid_request_get(self):
        """
        [GET] /firewall/blocked/1s
        :return: 404, not found
        """
        response = self.client.get(path="/firewall/blocked/1s")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_method(self):
        """
        [PUT] /firewall/blocked/1
        :return: 405, method not allowed
        """
        response = self.client.put(path="/firewall/blocked/1")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class BlockedIdPortTest(APITestCase):
    """
    [PUT] /firewall/blocked/{blockedId}/port
    """

    def test_valid_request_put(self):
        """
        [PUT] /firewall/blocked/1/port
        :return: 200, OK
        """
        response = self.client.put(path="/firewall/blocked/1/port", data={'rulePort': 20000})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rulePort'], 20000)

    def test_invalid_request_put_empty_body(self):
        """
        [PUT] /firewall/blocked/1/port
        :return: 400, bad request
        """
        response = self.client.put(path="/firewall/blocked/1/port")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_method(self):
        """
        [GET] /firewall/blocked/1/port
        :return: 405, method not allowed
        """
        response = self.client.get(path="/firewall/blocked/1/port")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class BlockedIdReasonTest(APITestCase):
    """
    [PUT] /firewall/blocked/{blockedId}/reason
    """

    def test_valid_request_put(self):
        """
        [PUT] /firewall/blocked/1/reason
        :return: 200, OK
        """
        response = self.client.put(path="/firewall/blocked/1/reason", data={'ruleReason': 'someReason'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ruleReason'], 'someReason')

    def test_invalid_request_put_empty_body(self):
        """
        [PUT] /firewall/blocked/24/reason
        :return: 400, bad request
        """
        response = self.client.put(path="/firewall/blocked/24/reason")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_method(self):
        """
        [GET] /firewall/blocked/38/reason
        :return: 405, method not allowed
        """
        response = self.client.get(path="/firewall/blocked/38/reason")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class BlockedIpTest(APITestCase):
    """
    [GET] /firewall/{blockedIp}

    [PUT] /firewall/{blockedIp}

    [DELETE] /firewall/{blockedIp}
    """

    def test_valid_request_get(self):
        """
        [GET] /firewall/147.251.15.15
        :return: 200, OK
        """
        response = self.client.get(path="/firewall/147.251.15.15")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['ruleIp'], '147.251.15.15')

    def test_valid_request_put(self):
        """
        [PUT] /firewall/147.251.15.16
        :return: 200, OK
        """
        response = self.client.put(path="/firewall/147.251.15.16", data={'ruleReason': 'someReason'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['ruleIp'], '147.251.15.16')
        self.assertEqual(response.data[0]['ruleReason'], 'someReason')

    def test_valid_request_delete(self):
        """
        [DELETE] /firewall/147.251.15.17
        :return: 200, OK
        """
        response = self.client.delete(path="/firewall/147.251.15.17")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_request_put_empty_body(self):
        """
        [PUT] /firewall/147.251.15.16
        :return: 400, bad request
        """
        response = self.client.put(path="/firewall/147.251.15.16")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_method(self):
        """
        [POST] /firewall/147.251.15.16
        :return: 405, method not allowed
        """
        response = self.client.post(path="/firewall/147.251.15.16")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_invalid_request_delete(self):
        """
        [DELETE] /firewall/147...
        :return: 404, not found
        """
        response = self.client.delete(path="/firewall/147...")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class BlockedIpBlockedPortTest(APITestCase):
    """
    [DELETE] /firewall/{blockedIp}/{blockedPort}
    """

    def test_valid_request_delete(self):
        """
        [DELETE] /firewall/147.251.11.11/20000
        :return: 200, OK
        """
        response = self.client.delete(path="/firewall/147.251.11.11/20000")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_method(self):
        """
        [DELETE] /firewall/147.251.11.11/20000
        :return: 405, method not allowed
        """
        response = self.client.get(path="/firewall/147.251.11.11/20000")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_invalid_delete(self):
        """
        [DELETE] /firewall/147..251.11.11/20000
        :return: 404, not found
        """
        response = self.client.delete(path="/firewall/147..251.11.11/20000")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
