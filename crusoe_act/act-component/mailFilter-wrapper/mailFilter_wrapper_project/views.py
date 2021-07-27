from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest

SERVICE_AVAILABLE = 0
FUNCTION_NOT_SUPPORTED = 0
ADDRESS_NOT_FOUND = 0
NO_EMAILS_BLOCKED_FROM = 0
NO_EMAILS_BLOCKED_TO = 0

SERVICE_UNAVAILABLE_MSG = "Service unavailable!"
FUNCTION_NOT_SUPPORTED_MSG = "Function not supported!"
ADDRESS_NOT_FOUND_MSG = "E-mail address not found!"
NO_EMAILS_BLOCKED_FROM_MSG = "No e-mails blocked in 'from' direction."
NO_EMAILS_BLOCKED_TO_MSG = "No e-mails blocked in 'to' direction."


class MailFilterHealthCheck(RetrieveAPIView):
    """
    [GET] /mailFilter/health

    Returns a health check for mail filter

    """

    def get(self, request, **kwargs):
        if SERVICE_AVAILABLE:
            return Response({"serviceStatus": "alive"})

        return Response(SERVICE_UNAVAILABLE_MSG, status=503)


class MailFilterCapacity(RetrieveAPIView):
    """
    [GET] /mailFilter/capacity

    Returns mail filter capacities for mail filter

    """

    def get(self, request, **kwargs):
        if FUNCTION_NOT_SUPPORTED:
            return HttpResponseForbidden(FUNCTION_NOT_SUPPORTED_MSG)

        return Response({
            "maxCapacity": 0,
            "usedCapacity": 0,
            "freeCapacity": 0
        })


class MailFilterBlockedList(APIView):
    """
    [GET] /mailFilter/blocked

    Returns a list of e-mail addresses blocked by mailFilter

    [POST] /mailFilter/blocked

    Block an e-mail address by mailFilter

    """

    def get(self, request, **kwargs):
        return Response([{
            "ruleId": 0,
            "ruleAddress": "string",
            "ruleFrom": True,
            "ruleTo": True,
            "ruleReason": "string"
        }])

    def post(self, request, **kwargs):
        if len(request.data) != 4:
            return HttpResponseBadRequest()

        return Response({
            "ruleId": 0
        })


class MailFilterBlockedRuleId(APIView):
    """
    [GET] /mailFilter/blocked/{ruleId}

    Get details of a rule with the ruleID from mailFilter

    [PUT] /mailFilter/blocked/{ruleId}

    Change a reason, from and to for a rule with ruleID on the mailFilter

    [DELETE] /mailFilter/blocked/{ruleId}

    Delete a rule with ruleId from the mailFilter
    """

    def get(self, request, ruleId, **kwargs):
        """
        :param ruleId: unlimited from 1 to n
        """
        return Response({
            "ruleId": int(ruleId),
            "ruleAddress": "string",
            "ruleFrom": True,
            "ruleTo": True,
            "ruleReason": "string"
        })

    def put(self, request, ruleId, **kwargs):
        """
        :param ruleId: unlimited from 1 to n
        """

        if len(request.data) != 3:
            return HttpResponseBadRequest()

        return Response({
            "ruleId": int(ruleId),
            "ruleAddress": "string",
            "ruleFrom": request.data['ruleFrom'] == 'True',
            "ruleTo": request.data['ruleTo'] == 'True',
            "ruleReason": request.data['ruleReason']
        })

    def delete(self, request, ruleId, **kwargs):
        """
        :param ruleId: unlimited from 1 to n
        """
        return Response({
            "ruleId": int(ruleId),
            "ruleAddress": "string",
            "ruleFrom": True,
            "ruleTo": True,
            "ruleReason": "string"
        })


class MailFilterRuleAddress(APIView):
    """
    [GET] /mailFilter/{ruleAddress}

    Get all rules with specified ruleAddress

    [PUT] /mailFilter/{ruleAddress}

    Change a reason and direction for all rules with the specified e-mail address

    [DELETE] /mailFilter/{ruleAddress}

    Delete all rules for specified e-mail address and direction (from or to)
    """

    def get(self, request, ruleAddress, **kwargs):
        """
        :param ruleAddress: e-mail address
        """
        if ADDRESS_NOT_FOUND:
            return HttpResponseNotFound(ADDRESS_NOT_FOUND_MSG)

        return Response([{
            "ruleId": 0,
            "ruleAddress": ruleAddress,
            "ruleFrom": True,
            "ruleTo": True,
            "ruleReason": "string"
        }])

    def put(self, request, ruleAddress, **kwargs):
        """
        :param ruleAddress: e-mail address
        """
        if ADDRESS_NOT_FOUND:
            return HttpResponseNotFound(ADDRESS_NOT_FOUND_MSG)

        if len(request.data) != 3:
            return HttpResponseBadRequest()

        return Response([{
            "ruleId": 0,
            "ruleAddress": ruleAddress,
            "ruleFrom": request.data['ruleFrom'] == 'True',
            "ruleTo": request.data['ruleTo'] == 'True',
            "ruleReason": request.data['ruleReason']
        }])

    def delete(self, request, ruleAddress, **kwargs):
        """
        :param ruleAddress: e-mail address
        """
        if ADDRESS_NOT_FOUND:
            return HttpResponseNotFound(ADDRESS_NOT_FOUND_MSG)

        return Response()


class MailFilterFrom(APIView):
    """
    [GET] /mailFilter/from

    Get all rules with specified ruleAddress in 'from' direction
    """

    def get(self, request, **kwargs):
        if NO_EMAILS_BLOCKED_FROM:
            return HttpResponseNotFound(NO_EMAILS_BLOCKED_FROM_MSG)

        return Response([{
            "ruleId": 0,
            "ruleAddress": "string",
            "ruleFrom": True,
            "ruleTo": True,
            "ruleReason": "string"
        }])


class MailFilterTo(APIView):
    """
    [GET] /mailFilter/to

    Get all rules with specified ruleAddress 'to' direction
    """

    def get(self, request, **kwargs):
        if NO_EMAILS_BLOCKED_TO:
            return HttpResponseNotFound(NO_EMAILS_BLOCKED_TO_MSG)

        return Response([{
            "ruleId": 0,
            "ruleAddress": "string",
            "ruleFrom": True,
            "ruleTo": True,
            "ruleReason": "string"
        }])
