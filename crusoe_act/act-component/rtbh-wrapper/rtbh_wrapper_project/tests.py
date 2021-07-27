from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse


class HealthTest(APITestCase):
    """
    [GET] /rtbh/health
    """

    def test_valid_request(self):
        """
        [GET] /rtbh/health
        :return: 200, OK
        """
        response = self.client.get(reverse("health_check"))
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_invalid_request(self):
        """
        [GET] /rtbh/health1234
        :return: 404, invalid url, not found
        """
        response = self.client.get(path="/rtbh/health1234")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_method(self):
        """
        [POST] /rtbh/health
        :return: 405, method POST not allowed
        """
        response = self.client.post(reverse("health_check"))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class CapacityTest(APITestCase):
    """
    [GET] /rtbh/capacity
    """

    def test_valid_request(self):
        """
        [GET] /rtbh/capacity
        :return: 200, OK
        """
        response = self.client.get(reverse("capacity"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_method(self):
        """
        [POST] /rtbh/capacity
        :return: 405, method POST not allowed
        """
        response = self.client.post(reverse("capacity"))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class BlockedTest(APITestCase):
    """
    [GET] /rtbh/blocked
    [POST] /rtbh/blocked
    """

    def test_valid_request_get(self):
        """
        [GET] /rtbh/blocked
        :return: 200, OK
        """
        response = self.client.get(reverse("blocked"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_valid_request_post(self):
        """
        [POST] /rtbh/blocked
        :return: 200, OK
        """
        response = self.client.post(reverse("blocked"), data={
            "ruleIp": "147.251.11.1",
            "ruleReason": "someReason"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ruleId'], 0)

    def test_invalid_request_post(self):
        """
        [POST] /rtbh/blocked
        :return: 400, bad request
        """
        response = self.client.post(reverse("blocked"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_method(self):
        """
        [DELETE] /rtbh/blocked
        :return: 405, method not allowed
        """
        response = self.client.delete(reverse("blocked"))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class BlockedIdTest(APITestCase):
    """
    [GET] /rtbh/blocked/{blockedId}
    [PUT] /rtbh/blocked/{blockedId}
    [DELETE] /rtbh/blocked/{blockedId}
    """

    def test_valid_request_get(self):
        """
        [GET] /rtbh/blocked/1
        :return: 200, OK
        """
        response = self.client.get(path="/rtbh/blocked/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ruleId'], 1)

    def test_valid_request_put(self):
        """
        [PUT] /rtbh/blocked/1
        :return: 200, OK
        """
        response = self.client.put(path="/rtbh/blocked/1", data={'ruleReason': 'someReason'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ruleReason'], 'someReason')

    def test_valid_request_delete(self):
        response = self.client.delete(path="/rtbh/blocked/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ruleId'], 1)

    def test_invalid_request_get(self):
        """
        [GET] /rtbh/blocked/1s
        :return: 404, not found
        """
        response = self.client.get(path="/rtbh/blocked/1s")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_request_put_empty_body(self):
        """
        [PUT] /rtbh/blocked/1
        :return: 400, bad request
        """
        response = self.client.put(path="/rtbh/blocked/1")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_method(self):
        """
        [POST] /rtbh/blocked/1
        :return: 405, method not allowed
        """
        response = self.client.post(path="/rtbh/blocked/1")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class BlockedIpTest(APITestCase):
    """
    [GET] /rtbh/{blockedIp}
    [PUT] /rtbh/{blockedIp}
    [DELETE] /rtbh/{blockedIp}
    """

    def test_valid_request_get(self):
        """
        [GET] /rtbh/147.251.15.15
        :return: 200, OK
        """
        response = self.client.get(path="/rtbh/147.251.15.15")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['ruleIp'], '147.251.15.15')

    def test_valid_request_put(self):
        """
        [PUT] /rtbh/147.251.15.16
        :return: 200, OK
        """
        response = self.client.put(path="/rtbh/147.251.15.16", data={'ruleReason': 'someReason'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['ruleIp'], '147.251.15.16')
        self.assertEqual(response.data[0]['ruleReason'], 'someReason')

    def test_valid_request_delete(self):
        """
        [DELETE] /rtbh/147.251.15.17
        :return: 200, OK
        """
        response = self.client.delete(path="/rtbh/147.251.15.17")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_request_put_empty_body(self):
        """
        [PUT] /rtbh/147.251.15.16
        :return: 400, bed request
        """
        response = self.client.put(path="/rtbh/147.251.15.16")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_method(self):
        """
        [GET] /rtbh/147.251.15.15
        :return: 405, method not allowed
        """
        response = self.client.post(path="/rtbh/147.251.15.16")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_invalid_request_delete(self):
        """
        [GET] /rtbh/147...
        :return: 404, not found
        """
        response = self.client.delete(path="/rtbh/147...")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
