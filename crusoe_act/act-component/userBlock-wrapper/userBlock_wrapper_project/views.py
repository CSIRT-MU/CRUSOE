from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest

SERVICE_AVAILABLE = 0
FUNCTION_NOT_SUPPORTED = 0
USER_NOT_FOUND = 0

SERVICE_UNAVAILABLE_MSG = "Service unavailable!"
FUNCTION_NOT_SUPPORTED_MSG = "Function not supported!"
USER_NOT_FOUND_MSG = "User not found!"


def get_blocked_to(ruleId):
    """
    Function obtains parameter 'blockedTo' from a rule with given id. Implementation of this function depends on how the
    rules are stored
    :param ruleId: ID of the rule
    :return: Returns value of the key 'ruleBlockedTo' from rule with given ID
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


class UserBlockHealthCheck(RetrieveAPIView):
    """
    [GET] /userBlock/health

    Returns a health check for user block interface with given id

    """

    def get(self, request, **kwargs):
        if SERVICE_AVAILABLE:
            return Response({"serviceStatus": "alive"})

        return Response(SERVICE_UNAVAILABLE_MSG, status=503)


class UserBlockCapacity(RetrieveAPIView):
    """
    [GET] /userBlock/capacity

    Returns a list of user block capacities for user block interface with given id

    """

    def get(self, request, **kwargs):
        if FUNCTION_NOT_SUPPORTED:
            return HttpResponseForbidden(FUNCTION_NOT_SUPPORTED_MSG)

        return Response({
            "maxCapacity": 0,
            "usedCapacity": 0,
            "freeCapacity": 0
        })


class UserBlockBlockedList(APIView):
    """
    [GET] /userBlock/blocked

    Returns a list of blocked users for userBlock

    [POST] /userBlock/blocked

    Block a user by userBlock

    """

    def get(self, request, **kwargs):
        return Response([{
            "ruleId": 0,
            "ruleUser": "string",
            "ruleBlockedFrom": "string",
            "ruleBlockedTo": "string",
            "ruleReason": "string"
        }])

    def post(self, request, **kwargs):
        if len(request.data) != 4:
            return HttpResponseBadRequest()

        return Response({
            "ruleId": 0
        })


class UserBlockBlockedRuleId(APIView):
    """
    [GET] /userBlock/blocked/{ruleId}

    Get details of a rule with ruleID from userBlock

    [PUT] /userBlock/blocked/{ruleId}

    Change a reason or date of the user block end for a rule with ruleID on the userBlock

    [DELETE] /userBlock/blocked/{ruleId}

    Delete a rule with ruleId from userBlock
    """

    def get(self, request, ruleId, **kwargs):
        """
        :param ruleId: unlimited from 1 to n
        """
        return Response({
            "ruleId": int(ruleId),
            "ruleUser": "string",
            "ruleBlockedFrom": "string",
            "ruleBlockedTo": "string",
            "ruleReason": "string"
        })

    def put(self, request, ruleId, **kwargs):
        """
        :param ruleId: unlimited from 1 to n
        """

        if len(request.data) < 1 or len(request.data) > 2:
            return HttpResponseBadRequest()

        try:
            blocked_to = request.data['ruleBlockedTo']
        except KeyError:
            blocked_to = get_blocked_to(ruleId)

        try:
            reason = request.data['ruleReason']
        except KeyError:
            reason = get_reason(ruleId)

        return Response({
            "ruleId": int(ruleId),
            "ruleUser": "string",
            "ruleBlockedFrom": "string",
            "ruleBlockedTo": blocked_to,
            "ruleReason": reason
        })

    def delete(self, request, ruleId, **kwargs):
        """
        :param ruleId: unlimited from 1 to n
        """
        return Response({
            "ruleId": int(ruleId),
            "ruleUser": "string",
            "ruleBlockedFrom": "string",
            "ruleBlockedTo": "string",
            "ruleReason": "string"
        })


class UserBlockUser(APIView):
    """
    [GET] /userBlock/{user}

    Get all rules with specified ruleAddress

    [PUT] /userBlock/{user}

    Change a reason and direction for all rules with the specified e-mail address

    [DELETE] /userBlock/{user}

    Delete all rules for specified e-mail address and direction (from or to)
    """

    def get(self, request, user, **kwargs):
        """
        :param user: any number of word characters
        """
        if USER_NOT_FOUND:
            return HttpResponseNotFound(USER_NOT_FOUND_MSG)

        return Response([{
            "ruleId": 0,
            "ruleUser": user,
            "ruleBlockedFrom": "string",
            "ruleBlockedTo": "string",
            "ruleReason": "string"
        }])

    def put(self, request, user, **kwargs):
        """
        :param user: any number of word characters
        """
        if USER_NOT_FOUND:
            return HttpResponseNotFound(USER_NOT_FOUND_MSG)

        if len(request.data) != 2:
            return HttpResponseBadRequest()

        return Response([{
            "ruleId": 0,
            "ruleUser": user,
            "ruleBlockedFrom": "string",
            "ruleBlockedTo": request.data['ruleBlockedTo'],
            "ruleReason": request.data['ruleReason']
        }])

    def delete(self, request, user, **kwargs):
        """
        :param user: any number of word characters
        """
        if USER_NOT_FOUND:
            return HttpResponseNotFound(USER_NOT_FOUND_MSG)

        return Response()
