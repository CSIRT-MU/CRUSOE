from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse


class HealthTest(APITestCase):
    """
    [GET] /userBlock/health
    """

    def test_valid_request(self):
        """
        [GET] /userBlock/health
        :return: 200, OK
        """
        response = self.client.get(reverse("health_check"))
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_invalid_method(self):
        """
        [POST] /userBlock/health
        :return: 405, method POST not allowed
        """
        response = self.client.post(reverse("health_check"))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class CapacityTest(APITestCase):
    """
    [GET] /userBlock/capacity
    """

    def test_valid_request(self):
        """
        [GET] /userBlock/capacity
        :return: 200, OK
        """
        response = self.client.get(reverse("capacity"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_method(self):
        """
        [POST] /userBlock/capacity
        :return: 405, method POST not allowed
        """
        response = self.client.post(reverse("capacity"))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class BlockedTest(APITestCase):
    """
    [GET] /userBlock/blocked
    [POST] /userBlock/blocked
    """

    def test_valid_request_get(self):
        """
        [GET] /userBlock/blocked
        :return: 200, OK
        """
        response = self.client.get(reverse("blocked"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_valid_request_post(self):
        """
        [POST] /userBlock/blocked
        :return: 200, OK
        """
        response = self.client.post(reverse("blocked"), data={
            "ruleUser": "user",
            "ruleBlockedFrom": "24.12.2020",
            "ruleBlockedTo": "25.12.2020",
            "ruleReason": "someReason"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ruleId'], 0)

    def test_invalid_request_post(self):
        """
        [POST] /userBlock/blocked
        :return: 400, bad request
        """
        response = self.client.post(reverse("blocked"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_method(self):
        """
        [DELETE] /userBlock/blocked
        :return: 405, method not allowed
        """
        response = self.client.delete(reverse("blocked"))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class BlockedIdTest(APITestCase):
    """
    [GET] /userBlock/blocked/{blockedId}
    [PUT] /userBlock/blocked/{blockedId}
    [DELETE] /userBlock/blocked/{blockedId}
    """

    def test_valid_request_get(self):
        """
        [GET] /userBlock/blocked/1
        :return: 200, OK
        """
        response = self.client.get(path="/userBlock/blocked/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ruleId'], 1)

    def test_valid_request_put(self):
        """
        [PUT] /userBlock/blocked/1
        :return: 200, OK
        """
        response = self.client.put(path="/userBlock/blocked/1",
                                   data={
                                       "ruleBlockedTo": "1.1.2021",
                                       "ruleReason": "someReason"
                                   })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ruleBlockedTo'], '1.1.2021')
        self.assertEqual(response.data['ruleReason'], 'someReason')

    def test_valid_request_put_missing_attributes(self):
        """
        [PUT] /userBlock/blocked/1
        :return: 200, OK
        """
        response = self.client.put(path="/userBlock/blocked/1",
                                   data={
                                       "ruleBlockedTo": "1.1.2021"
                                   })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ruleBlockedTo'], '1.1.2021')

    def test_valid_request_delete(self):
        """
        [DELETE] /userBlock/blocked/1
        :return: 200, OK
        """
        response = self.client.delete(path="/userBlock/blocked/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ruleId'], 1)

    def test_invalid_request_put_empty_body(self):
        """
        [PUT] /userBlock/blocked/1
        :return: 400, bad request
        """
        response = self.client.put(path="/userBlock/blocked/1")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_method(self):
        """
        [POST] /userBlock/blocked/1
        :return: 405, method not allowed
        """
        response = self.client.post(path="/userBlock/blocked/1")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class UserTest(APITestCase):
    """
    [GET] /userBlock/{user}
    [PUT] /userBlock/{user}
    [DELETE] /userBlock/{user}
    """

    def test_valid_request_get(self):
        """
        [GET] /userBlock/someUser
        :return: 200, OK
        """
        response = self.client.get(path="/userBlock/someUser")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['ruleUser'], 'someUser')

    def test_valid_request_put(self):
        """
        [PUT] /userBlock/someUser
        :return: 200, OK
        """
        response = self.client.put(path="/userBlock/someUser", data={'ruleBlockedTo': '1.1.2021',
                                                                     'ruleReason': 'someReason'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['ruleUser'], 'someUser')
        self.assertEqual(response.data[0]['ruleBlockedTo'], '1.1.2021')
        self.assertEqual(response.data[0]['ruleReason'], 'someReason')

    def test_valid_request_delete(self):
        """
        [DELETE] /userBlock/someUser
        :return: 200, OK
        """
        response = self.client.delete(path="/userBlock/someUser")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_request_put_empty_body(self):
        """
        [PUT] /userBlock/someUser
        :return: 400, bad request
        """
        response = self.client.put(path="/userBlock/someUser")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_method(self):
        """
        [POST] /userBlock/someUser
        :return: 405, method not allowed
        """
        response = self.client.post(path="/userBlock/someUser")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
