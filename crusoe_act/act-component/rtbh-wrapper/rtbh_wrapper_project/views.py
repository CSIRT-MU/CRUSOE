from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest

SERVICE_AVAILABLE = 0
FUNCTION_NOT_SUPPORTED = 0
IP_NOT_FOUND = 0

SERVICE_UNAVAILABLE_MSG = "Service unavailable!"
FUNCTION_NOT_SUPPORTED_MSG = "Function not supported!"
IP_NOT_FOUND_MSG = "Ip not found!"


class RtbhHealthCheck(RetrieveAPIView):
    """
    [GET] /rtbh/health

    Returns a health check for rtbh
    """

    def get(self, request, **kwargs):
        if SERVICE_AVAILABLE:
            return Response({"serviceStatus": "alive"})

        return Response(SERVICE_UNAVAILABLE_MSG, status=503)


class RtbhCapacity(RetrieveAPIView):
    """
    [GET] /rtbh/capacity

    Returns capacities for rtbh
    """

    def get(self, request, **kwargs):
        if FUNCTION_NOT_SUPPORTED:
            return HttpResponseForbidden(FUNCTION_NOT_SUPPORTED_MSG)

        return Response({
            "maxCapacity": 0,
            "usedCapacity": 0,
            "freeCapacity": 0
        })


class RtbhBlockedList(APIView):
    """
    [GET] /rtbh/blocked

    Returns a list of blocked IP addresses for RTBH interface

    [POST] /rtbh/blocked

    Block an IP on RTBH interface
    """

    def get(self, request, **kwargs):
        return Response([{
            "ruleId": 0,
            "ruleIp": "string",
            "ruleReason": "string"
        }])

    def post(self, request, **kwargs):

        if len(request.data) != 2:
            return HttpResponseBadRequest()

        return Response({
            "ruleId": 0
        })


class RtbhBlockedId(APIView):
    """
    [GET] /rtbh/blocked/{blockedId}

    Get details of a rule with ruleID from RTBH

    [PUT] /rtbh/blocked/{blockedId}

    Change a reason for a rule with ruleID on the RTBH

    [DELETE] /rtbh/blocked/{blockedId}

    Delete a rule with blockedId from RTBH
    """

    def get(self, request, blockedId, **kwargs):
        """
        :param blockedId: unlimited from 1 to n
        """
        return Response({
            "ruleId": int(blockedId),
            "ruleIp": "string",
            "ruleReason": "string"
        })

    def put(self, request, blockedId, **kwargs):
        """
        :param blockedId: unlimited from 1 to n
        """

        if len(request.data) != 1:
            return HttpResponseBadRequest()

        return Response({
            "ruleId": int(blockedId),
            "ruleIp": "string",
            "ruleReason": request.data['ruleReason']
        })

    def delete(self, request, blockedId, **kwargs):
        """
        :param blockedId: unlimited from 1 to n
        """
        return Response({
            "ruleId": int(blockedId),
            "ruleIp": "string",
            "ruleReason": "string"
        })


class RtbhBlockedIp(APIView):
    """
    [GET] /rtbh/{blockedIp}

    Get all rules with specified blockedIp on RTBH

    [PUT] /rtbh/{blockedIp}

    Change the reason for all rules with specified IP

    [DELETE] /rtbh/{blockedIp}

    Delete all rules for specified IP
    """

    def get(self, request, blockedIp, **kwargs):
        """
        :param blockedIp: any ipv4
        """
        if IP_NOT_FOUND:
            return HttpResponseNotFound(IP_NOT_FOUND_MSG)

        return Response([{
            "ruleId": 0,
            "ruleIp": blockedIp,
            "ruleReason": "string"
        }])

    def put(self, request, blockedIp, **kwargs):
        """
        :param blockedIp: any ipv4
        """
        if IP_NOT_FOUND:
            return HttpResponseNotFound(IP_NOT_FOUND_MSG)

        if len(request.data) != 1:
            return HttpResponseBadRequest()

        return Response([{
            "ruleId": 0,
            "ruleIp": blockedIp,
            "ruleReason": request.data['ruleReason']
        }])

    def delete(self, request, blockedIp, **kwargs):
        """
        :param blockedIp: any ipv4
        """
        if IP_NOT_FOUND:
            return HttpResponseNotFound(IP_NOT_FOUND_MSG)

        return Response()
