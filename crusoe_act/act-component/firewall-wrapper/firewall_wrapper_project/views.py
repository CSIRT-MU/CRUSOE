from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, DestroyAPIView
from django.http import HttpResponseForbidden, HttpResponseNotFound, HttpResponseBadRequest

IP_NOT_FOUND = 0
PORT_NOT_FOUND = 0
SERVICE_AVAILABLE = 0
FUNCTION_NOT_SUPPORTED = 0

IP_NOT_FOUND_MSG = "IP not found!"
PORT_NOT_FOUND_MSG = "Port not found!"
SERVICE_UNAVAILABLE_MSG = "Service unavailable!"
FUNCTION_NOT_SUPPORTED_MSG = "Function not supported!"


class FwHealthCheck(RetrieveAPIView):
    """
    [GET] /firewall/health

    Returns a health check for firewall

    """

    def get(self, request, **kwargs):
        if SERVICE_AVAILABLE:
            return Response({"serviceStatus": "alive"})

        return Response(SERVICE_UNAVAILABLE_MSG, status=503)


class FwCapacity(RetrieveAPIView):
    """
    [GET] /firewall/capacity

    Returns capacities for firewall

    """

    def get(self, request, **kwargs):
        if FUNCTION_NOT_SUPPORTED:
            return HttpResponseForbidden(FUNCTION_NOT_SUPPORTED_MSG)

        return Response({
            "maxCapacity": 0,
            "usedCapacity": 0,
            "freeCapacity": 0
        })


class FwBlockedList(APIView):
    """
    [GET] /firewall/blocked

    Returns a list of blocked IP adresses for firewall

    [POST] /firewall/blocked

    Block an IP on firewall, port is optional

    """

    def get(self, request, **kwargs):
        return Response([{
            "ruleId": 0,
            "ruleIp": "string",
            "rulePort": 0,
            "ruleReason": "string"
        }])

    def post(self, request, **kwargs):

        if len(request.data) != 3:
            return HttpResponseBadRequest()

        return Response({
            "ruleId": 0
        })


class FwBlockedId(APIView):
    """
    [GET] /firewall/blocked/{blockedId}

    Get details of a rule with ruleID from firewall

    [DELETE] /firewall/blocked/{blockedId}

    Delete a rule with blockedId from firewall

    """

    def get(self, request, blockedId, **kwargs):
        return Response({
            "ruleId": int(blockedId),
            "ruleIp": "string",
            "rulePort": 0,
            "ruleReason": "string"
        })

    def delete(self, request, blockedId, **kwargs):
        return Response({
            "ruleId": int(blockedId),
            "ruleIp": "string",
            "rulePort": 0,
            "ruleReason": "string"
        })


class FwBlockedIdPort(APIView):
    """
    [PUT] /firewall/blocked/{blockedId}/port

    Change port for a rule with ruleID on the firewall

    """

    def put(self, request, blockedId, **kwargs):

        if len(request.data) != 1:
            return HttpResponseBadRequest()

        return Response({
            "ruleId": int(blockedId),
            "ruleIp": "string",
            "rulePort": int(request.data['rulePort']),
            "ruleReason": "string"
        })


class FwBlockedIdReason(APIView):
    """
    [PUT] /firewall/blocked/{blockedId}/reason

    Change reason for a rule with ruleID on the firewall

    """

    def put(self, request, blockedId, **kwargs):

        if len(request.data) != 1:
            return HttpResponseBadRequest()

        return Response({
            "ruleId": blockedId,
            "ruleIp": "string",
            "rulePort": 0,
            "ruleReason": request.data['ruleReason']
        })


class FwBlockedIp(APIView):
    """
    [GET] /firewall/{blockedIp}

    Get all rules with specified blockedIp on firewall

    [PUT] /firewall/{blockedIp}

    Change the reason for all rules with specified IP

    [DELETE] /firewall/{blockedIp}

    Delete all rules for IP
    """

    def get(self, request, blockedIp, **kwargs):
        if IP_NOT_FOUND:
            return HttpResponseNotFound(IP_NOT_FOUND_MSG)

        return Response([{
            "ruleId": 0,
            "ruleIp": blockedIp,
            "rulePort": 0,
            "ruleReason": "string"
        }])

    def put(self, request, blockedIp, **kwargs):

        if len(request.data) != 1:
            return HttpResponseBadRequest()

        if IP_NOT_FOUND:
            return HttpResponseNotFound(IP_NOT_FOUND_MSG)

        return Response([{
                "ruleId": 0,
                "ruleIp": blockedIp,
                "rulePort": 0,
                "ruleReason": request.data['ruleReason']
            }])

    def delete(self, request, blockedIp, **kwargs):
        if IP_NOT_FOUND:
            return HttpResponseNotFound(IP_NOT_FOUND_MSG)

        return Response()


class FwBlockedIpBlockedPort(DestroyAPIView):
    """
    [DELETE] /firewall/{blockedIp}/{blockedPort}

    Delete a rule containing the IP and port

    """

    def delete(self, request, **kwargs):
        if IP_NOT_FOUND:
            return HttpResponseNotFound(IP_NOT_FOUND_MSG)
        if PORT_NOT_FOUND:
            return HttpResponseNotFound(PORT_NOT_FOUND)

        return Response()
