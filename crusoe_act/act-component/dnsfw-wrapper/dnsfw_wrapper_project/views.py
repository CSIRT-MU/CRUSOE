from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest

DOMAIN_NOT_FOUND = 0
SERVICE_AVAILABLE = 0
FUNCTION_NOT_SUPPORTED = 0

DOMAIN_NOT_FOUND_MSG = "Domain not found!"
SERVICE_UNAVAILABLE_MSG = "Service unavailable!"
FUNCTION_NOT_SUPPORTED_MSG = "Function not supported!"


def get_zone(ruleId):
    """
    Function obtains parameter 'zone' from a rule with given id. Implementation of this function depends on how the rules
    are stored
    :param ruleId: ID of the rule
    :return: Returns value of the key 'ruleZone' from rule with given ID
    """
    return "default"


def get_target(ruleId):
    """
    Function obtains parameter 'target' from a rule with given id. Implementation of this function depends on how the
    rules are stored
    :param ruleId: ID of the rule
    :return: Returns value of the key 'ruleTarget' from rule with given ID
    """
    return "default"


def get_reason(ruleId):
    """
    Function obtains parameter 'reason' from a rule with given id. Implementation of this function depends on how rules are
    stored
    :param ruleId: ID of the rule
    :return: Returns value of the key 'ruleReason' from rule with given ID
    """
    return "default"


def get_note(ruleId):
    """
    Function obtains parameter 'note' from a rule with given id. Implementation of this function depends on how rules are
    stored
    :param ruleId: ID of the rule
    :return: Returns value of the key 'ruleNote' from rule with given ID
    """
    return "default"


class DnsHealthCheck(RetrieveAPIView):
    """
    [GET] /dnsfw/health

    Returns a health check for the DNS FW
    """

    def get(self, request, **kwargs):
        if SERVICE_AVAILABLE:
            return Response({"serviceStatus": "alive"})

        return Response(SERVICE_UNAVAILABLE_MSG, status=503)


class DnsCapacity(RetrieveAPIView):
    """
    [GET] /dnsfw/capacity

    Returns DNS FW capacities
    """

    def get(self, request, **kwargs):
        if FUNCTION_NOT_SUPPORTED:
            return HttpResponseForbidden(FUNCTION_NOT_SUPPORTED_MSG)

        return Response({
            "maxCapacity": 0,
            "usedCapacity": 0,
            "freeCapacity": 0
        })


class DnsRulesList(APIView):
    """
    [GET] /dnsfw/rules

    Returns a list of all DNS FW rules

    [POST] /dnsfw/rules

    Add DNS FW rule to a DNS FW
    """

    def get(self, request, **kwargs):
        return Response([{
            "ruleId": 0,
            "ruleZone": "string",
            "ruleDomain": "string",
            "ruleTarget": "string",
            "ruleReason": "string",
            "ruleNote": "string"
        }])

    def post(self, request, **kwargs):

        if len(request.data) != 5:
            return HttpResponseBadRequest()

        return Response({
            "ruleId": 0
        })


class DnsRulesId(APIView):
    """
    [GET] /dnsfw/rules/{ruleId}

    Get details of a rule with ruleID from a DNS FW

    [PUT] /dnsfw/rules/{ruleId}

    Change a reason, or zone or target for a rule with ruleID from a DNS FW

    [DELETE] /dnsfw/rules/{ruleId}

    Delete a rule with ruleId from a DNS FW
    """

    def get(self, request, ruleId, **kwargs):
        """
        :param ruleId: unlimited from 1 to n
        """
        return Response({
            "ruleId": int(ruleId),
            "ruleZone": "string",
            "ruleDomain": "string",
            "ruleTarget": "string",
            "ruleReason": "string",
            "ruleNote": "string"
        })

    def put(self, request, ruleId, **kwargs):
        """
        :param ruleId: unlimited from 1 to n
        """
        if len(request.data) < 1 or len(request.data) > 4:
            return HttpResponseBadRequest()

        try:
            zone = request.data['ruleZone']
        except KeyError:
            zone = get_zone(ruleId)

        try:
            target = request.data['ruleTarget']
        except KeyError:
            target = get_target(ruleId)

        try:
            reason = request.data['ruleReason']
        except KeyError:
            reason = get_reason(ruleId)

        try:
            note = request.data['ruleNote']
        except KeyError:
            note = get_note(ruleId)

        return Response({
            "ruleId": int(ruleId),
            "ruleZone": zone,
            "ruleDomain": "string",
            "ruleTarget": target,
            "ruleReason": reason,
            "ruleNote": note
        })

    def delete(self, request, ruleId, **kwargs):
        """
        :param ruleId: unlimited from 1 to n
        """
        return Response({
            "ruleId": int(ruleId),
            "ruleZone": "string",
            "ruleDomain": "string",
            "ruleTarget": "string",
            "ruleReason": "string",
            "ruleNote": "string"
        })


class DnsRuleDomain(APIView):
    """
    [GET] /dnsfw/{ruleDomain}

    Get all rules with the specified ruleDomain from a DNS FW

    [PUT] /dnsfw/{ruleDomain}

    Change a zone or target or reason or note for all rules with the specified ruleDomain

    [DELETE] /dnsfw/{ruleDomain}

    Delete all rules for the specified ruleDomain
    """

    def get(self, request, domain, **kwargs):
        """
        :param domain: limited to from one to many non-digit characters, this can be changed in ./urls.py
        """
        if DOMAIN_NOT_FOUND:
            return HttpResponseNotFound(DOMAIN_NOT_FOUND_MSG)

        return Response([{
            "ruleId": 0,
            "ruleZone": "string",
            "ruleDomain": domain,
            "ruleTarget": "string",
            "ruleReason": "string",
            "ruleNote": "string"
        }])

    def put(self, request, domain, **kwargs):
        """
        Change a zone or target or reason or note, if not all of these are given, rest of the attributes
        will be obtained from a rule using its id.

        E.g. request.data = { 'ruleZone':'zone', 'ruleTarget':'target' }
        for each rule with given domain:
            rule[missing_attribute] = get_'missing_attribute'(rule.id)
            where missing_attribute in {['ruleZone'], ['ruleTarget'], ['ruleReason'], ['ruleNote']}

        :param domain: limited to from one to many non-digit characters, this can be changed in ./urls.py
        """
        if DOMAIN_NOT_FOUND:
            return HttpResponseNotFound(DOMAIN_NOT_FOUND_MSG)

        if len(request.data) < 1 or len(request.data) > 4:
            return HttpResponseBadRequest()

        try:
            zone = request.data['ruleZone']
        except KeyError:
            zone = get_zone(domain)

        try:
            target = request.data['ruleTarget']
        except KeyError:
            target = get_target(domain)

        try:
            reason = request.data['ruleReason']
        except KeyError:
            reason = get_reason(domain)

        try:
            note = request.data['ruleNote']
        except KeyError:
            note = get_note(domain)

        return Response([{
            "ruleId": 0,
            "ruleZone": zone,
            "ruleDomain": domain,
            "ruleTarget": target,
            "ruleReason": reason,
            "ruleNote": note
        }])

    def delete(self, request, domain, **kwargs):
        """
        :param domain: limited to from one to many non-digit characters, this can be changed in ./urls.py
        """
        if DOMAIN_NOT_FOUND:
            return HttpResponseNotFound(DOMAIN_NOT_FOUND_MSG)

        return Response()
