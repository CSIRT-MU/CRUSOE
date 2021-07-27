from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse


class HealthTest(APITestCase):
    """
    [GET] /mailFilter/health
    """

    def test_valid_request(self):
        """
        [GET] /mailFilter/health
        :return: 200, OK
        """
        response = self.client.get(reverse("health_check"))
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_invalid_request(self):
        """
        [GET] /mailFilter/health1234
        :return: 404, invalid url, not found
        """
        response = self.client.get(path="/rtbh/health1234")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_method(self):
        """
        [POST] /mailFilter/health
        :return: 405, method POST not allowed
        """
        response = self.client.post(reverse("health_check"))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class CapacityTest(APITestCase):
    """
    [GET] /mailFilter/capacity
    """

    def test_valid_request(self):
        """
        [GET] /mailFilter/capacity
        :return: 200, OK
        """
        response = self.client.get(reverse("capacity"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_method(self):
        """
        [POST] /mailFilter/capacity
        :return: 405, method POST not allowed
        """
        response = self.client.post(reverse("capacity"))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class BlockedTest(APITestCase):
    """
    [GET] /mailFilter/blocked
    [POST] /mailFilter/blocked
    """

    def test_valid_request_get(self):
        """
        [GET] /mailFilter/blocked
        :return: 200, OK
        """
        response = self.client.get(reverse("blocked"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_valid_request_post(self):
        """
        [POST] /mailFilter/blocked
        :return: 200, OK
        """
        response = self.client.post(reverse("blocked"), data={
            "ruleAddress": "milan.ziaran@gmail.com",
            "ruleFrom": True,
            "ruleTo": True,
            "ruleReason": "someReason"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ruleId'], 0)

    def test_invalid_request_post(self):
        """
        [POST] /mailFilter/blocked
        :return: 400, bad request
        """
        response = self.client.post(reverse("blocked"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_method(self):
        """
        [DELETE] /mailFilter/blocked
        :return: 405, method not allowed
        """
        response = self.client.delete(reverse("blocked"))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class BlockedIdTest(APITestCase):
    """
    [GET] /mailFilter/blocked/{blockedId}
    [PUT] /mailFilter/blocked/{blockedId}
    [DELETE] /mailFilter/blocked/{blockedId}
    """

    def test_valid_request_get(self):
        """
        [GET] /mailFilter/blocked/1
        :return: 200, OK
        """
        response = self.client.get(path="/mailFilter/blocked/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ruleId'], 1)

    def test_valid_request_put(self):
        """
        [PUT] /mailFilter/blocked/1
        :return: 200, OK
        """
        response = self.client.put(path="/mailFilter/blocked/1",
                                   data={'ruleFrom': True, 'ruleTo': True, 'ruleReason': 'someReason'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ruleFrom'], True)
        self.assertEqual(response.data['ruleTo'], True)
        self.assertEqual(response.data['ruleReason'], 'someReason')

    def test_valid_request_delete(self):
        """
        [DELETE] /mailFilter/blocked/1
        :return: 200, OK
        """
        response = self.client.delete(path="/mailFilter/blocked/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ruleId'], 1)

    def test_invalid_request_get(self):
        """
        [GET] /mailFilter/blocked/1s
        :return: 404, not found
        """
        response = self.client.get(path="/mailFilter/blocked/1s")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_request_put_empty_body(self):
        """
        [PUT] /mailFilter/blocked/1
        :return: 400, bad request
        """
        response = self.client.put(path="/mailFilter/blocked/1")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_method(self):
        """
        [POST] /mailFilter/blocked/1
        :return: 405, method not allowed
        """
        response = self.client.post(path="/mailFilter/blocked/1")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class RuleAddressTest(APITestCase):
    """
    [GET] /mailFilter/{ruleAddress}
    [PUT] /mailFilter/{ruleAddress}
    [DELETE] /mailFilter/{ruleAddress}
    """

    def test_valid_request_get(self):
        """
        [GET] /mailFilter/sample@example.com
        :return: 200, OK
        """
        response = self.client.get(path="/mailFilter/sample@example.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['ruleAddress'], 'sample@example.com')

    def test_valid_request_put(self):
        """
        [PUT] /mailFilter/example@example.com
        :return: 200, OK
        """
        response = self.client.put(path="/mailFilter/example@example.com", data={'ruleFrom': True,
                                                                                 'ruleTo': False,
                                                                                 'ruleReason': 'someReason'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['ruleAddress'], 'example@example.com')
        self.assertEqual(response.data[0]['ruleFrom'], True)
        self.assertEqual(response.data[0]['ruleTo'], False)
        self.assertEqual(response.data[0]['ruleReason'], 'someReason')

    def test_valid_request_delete(self):
        """
        [DELETE] /mailFilter/sample@example.com
        :return: 200, OK
        """
        response = self.client.delete(path="/mailFilter/example@example.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_request_put_empty_body(self):
        """
        [PUT] /mailFilter/sample@sample.com
        :return: 400, bad request
        """
        response = self.client.put(path="/mailFilter/example@sample.com")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_method(self):
        """
        [POST] /mailFilter/milan.ziaran@gmail.com
        :return: 405, method not allowed
        """
        response = self.client.post(path="/mailFilter/milan.ziaran@gmail.com")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_invalid_request_delete(self):
        """
        [GET] /mailFilter/...
        :return: 404, not found
        """
        response = self.client.delete(path="/mailFilter/...")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class FromTest(APITestCase):
    """
    [GET] /mailFilter/from
    """

    def test_valid_request_get(self):
        """
        [GET] /mailFilter/from
        :return: 200, OK
        """
        response = self.client.get(reverse("from"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_method(self):
        """
        [POST] /mailFilter/from
        :return: 405, method POST not allowed
        """
        response = self.client.post(reverse("from"))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_invalid_request_get(self):
        """
        [GET] /mailFilter/from
        :return: 404, not found
        """
        response = self.client.get(path="/mailFilter/froom")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ToTest(APITestCase):
    """
    [GET] /mailFilter/to
    """
    def test_valid_request_get(self):
        """
        [GET] /mailFilter/to
        :return: 200, OK
        """
        response = self.client.get(reverse("to"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_method(self):
        """
        [POST] /mailFilter/to
        :return: 405, method POST not allowed
        """
        response = self.client.post(reverse("to"))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_invalid_request_get(self):
        """
        [GET] /mailFilter/too
        :return: 404, not found
        """
        response = self.client.get(path="/mailFilter/too")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
