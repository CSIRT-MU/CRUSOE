from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse


class HealthTest(APITestCase):
    """
    [GET] /dnsfw/health
    """

    def test_valid_request(self):
        """
        [GET] /dnsfw/health
        :return: 200, OK
        """
        response = self.client.get(reverse("health_check"))
        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_invalid_method(self):
        """
        [POST] /dnsfw/health
        :return: 405, method POST not allowed
        """
        response = self.client.post(reverse("health_check"))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class CapacityTest(APITestCase):
    """
    [GET] /dnsfw/capacity
    """

    def test_valid_request(self):
        """
        [GET] /dnsfw/capacity
        :return: 200, OK
        """
        response = self.client.get(reverse("capacity"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_method(self):
        """
        [POST] /dnsfw/capacity
        :return: 405, method POST not allowed
        """
        response = self.client.post(reverse("capacity"))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class RulesTest(APITestCase):
    """
    [GET] /dnsfw/rules
    [POST] /dnsfw/rules
    """

    def test_valid_request_get(self):
        """
        [GET] /dnsfw/rules
        :return: 200, OK
        """
        response = self.client.get(reverse("rules"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_valid_request_post(self):
        """
        [POST] /dnsfw/rules
        :return: 200, OK
        """
        response = self.client.post(reverse("rules"), data={
            "ruleZone": "string",
            "ruleDomain": "string",
            "ruleTarget": "string",
            "ruleReason": "string",
            "ruleNote": "string"
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ruleId'], 0)

    def test_invalid_request_post_empty_body(self):
        """
        [POST] /dnsfw/rules
        :return: 400, bad request
        """
        response = self.client.post(reverse("rules"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RulesIdTest(APITestCase):
    """
    [GET] /dnsfw/rules/{ruleId}
    [PUT] /dnsfw/rules/{ruleId}
    [DELETE] /dnsfw/rules/{ruleId}
    """

    def test_valid_request_get(self):
        """
        [GET] /dnsfw/rules/1
        :return: 200, OK
        """
        response = self.client.get(path="/dnsfw/rules/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ruleId'], 1)

    def test_valid_request_put_missing_attributes(self):
        """
        [PUT] /dnsfw/rules/1
        :return: 200, OK
        """
        # missing ruleTarget, ruleReason and ruleNote
        response = self.client.put(path="/dnsfw/rules/1", data={'ruleZone': 'zone'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ruleZone'], 'zone')

    def test_valid_request_delete(self):
        """
        [DELETE] /dnsfw/rules/1
        :return: 200, OK
        """
        response = self.client.delete(path="/dnsfw/rules/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['ruleId'], 1)

    def test_invalid_request_put(self):
        """
        [PUT] /dnsfw/rules/1
        :return: 400, bad request
        """
        response = self.client.put(path="/dnsfw/rules/1")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RulesDomainTest(APITestCase):
    """
    [GET] /dnsfw/{ruleDomain}
    [PUT] /dnsfw/{ruleDomain}
    [DELETE] /dnsfw/{ruleDomain}
    """

    def test_valid_request_get(self):
        """
        [GET] /dnsfw/domain.com
        :return: 200, OK
        """
        response = self.client.get(path="/dnsfw/domain.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['ruleDomain'], 'domain.com')

    def test_valid_request_put(self):
        """
        [PUT] /dnsfw/domain.com
        :return: 200, OK
        """
        response = self.client.put(path="/dnsfw/domain.com", data={'ruleTarget': 'target'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['ruleTarget'], 'target')
        self.assertEqual(response.data[0]['ruleDomain'], 'domain.com')

    def test_valid_request_delete(self):
        """
        [DELETE] /dnsfw/domain.com
        :return: 200, OK
        """
        response = self.client.delete(path="/dnsfw/domain.com")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_method(self):
        """
        [POST] /dnsfw/domain.com
        :return: 405, method not allowed
        """
        response = self.client.post(path="/dnsfw/domain.com")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_invalid_request_put_empty_body(self):
        """
        [PUT] /dnsfw/domain.com
        :return: 400, bad request
        """
        response = self.client.put(path="/dnsfw/domain.com")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_request_delete(self):
        """
        [DELETE] /dnsfw/domain..com
        :return: 404, not found
        """
        response = self.client.delete(path="/dnsfw/domain..com")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
