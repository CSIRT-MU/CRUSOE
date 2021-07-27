import os
import json
import random

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, DestroyAPIView
from django.http import HttpResponseNotFound, HttpResponseBadRequest

IP_NOT_FOUND = 0
PORT_NOT_FOUND = 0
SERVICE_AVAILABLE = 0
FUNCTION_NOT_SUPPORTED = 0

IP_NOT_FOUND_MSG = "IP not found!"
PORT_NOT_FOUND_MSG = "Port not found!"
SERVICE_UNAVAILABLE_MSG = "Service unavailable!"
FUNCTION_NOT_SUPPORTED_MSG = "Function not supported!"
PATH = '/var/www/simulated-pao-firewall/firewall_wrapper_project/simulated-pao-firewall'


class FwHealthCheck(RetrieveAPIView):
    """
    [GET] /firewall/health

    Returns a health check for firewall

    """

    def get(self, request, **kwargs):
        if os.path.exists(PATH):
            return Response({"serviceStatus": "alive"})
        else:
            return Response(SERVICE_UNAVAILABLE_MSG, status=503)


class FwCapacity(RetrieveAPIView):
    """
    [GET] /firewall/capacity

    Returns capacities for firewall

    """

    def get(self, request, **kwargs):
        with open(PATH, 'r') as fw_json:
            data = json.load(fw_json)
            max_capacity = data['maxCapacity']
            used_capacity = len(data['blacklist'])
            free_capacity = max_capacity - used_capacity

        return Response({
            "maxCapacity": max_capacity,
            "usedCapacity": used_capacity,
            "freeCapacity": free_capacity
        })


class FwBlockedList(APIView):
    """
    [GET] /firewall/blocked

    Returns a list of blocked IP adresses for firewall

    [POST] /firewall/blocked

    Block an IP on firewall, port is optional

    """

    def get(self, request, **kwargs):
        with open(PATH, 'r') as fw_json:
            data = json.load(fw_json)
            return Response(data['blacklist'])

    def post(self, request, **kwargs):

        if len(request.data) != 3:
            return HttpResponseBadRequest()

        with open(PATH, 'r') as fw_json:
            data = json.load(fw_json)
            # check if ip is already blocked
            given_ip = request.data['ip']
            if check_ip(data, given_ip):
                return HttpResponseBadRequest(f"{given_ip} is already blocked.")
            new_id = random.randint(1, 1000)
            # check if id already exists
            while check_id(data, new_id):
                new_id = random.randint(1, 1000)
            data['blacklist'].append(request.data)
            data['blacklist'][len(data['blacklist']) - 1]['id'] = new_id
            # new_id = data['blacklist'][len(data['blacklist']) - 1]["id"] = len(data['blacklist'])
        with open(PATH, 'w') as fw_json:
            json.dump(data, fw_json)
        return Response({
            "ruleId": new_id
        })


class FwBlockedId(APIView):
    """
    [GET] /firewall/blocked/{blockedId}

    Get details of a rule with ruleID from firewall

    [DELETE] /firewall/blocked/{blockedId}

    Delete a rule with blockedId from firewall

    """

    def get(self, request, blocked_id, **kwargs):
        with open(PATH, 'r') as fw_json:
            data = json.load(fw_json)
            try:
                for rule in data['blacklist']:
                    if rule['id'] == blocked_id:
                        return Response(rule)
            except KeyError as e:
                return HttpResponseBadRequest(e)
            return HttpResponseNotFound(f"ID {blocked_id} not found")

    def delete(self, request, blocked_id, **kwargs):
        with open(PATH, 'r') as fw_json:
            data = json.load(fw_json)
            try:
                for rule in data['blacklist']:
                    if rule['id'] == blocked_id:
                        data['blacklist'].remove(rule)
                        break
            except KeyError as e:
                return HttpResponseNotFound(e)
        with open(PATH, 'w') as fw_json:
            json.dump(data, fw_json)

        return Response(rule)


class FwBlockedIdPort(APIView):
    """
    [PUT] /firewall/blocked/{blockedId}/port

    Change port for a rule with ruleID on the firewall

    """

    def put(self, request, blocked_id, **kwargs):

        if len(request.data) != 1:
            return HttpResponseBadRequest()

        return Response({
            "ruleId": int(blocked_id),
            "ruleIp": "string",
            "rulePort": int(request.data['rulePort']),
            "ruleReason": "string"
        })


class FwBlockedIdReason(APIView):
    """
    [PUT] /firewall/blocked/{blockedId}/reason

    Change reason for a rule with ruleID on the firewall

    """

    def put(self, request, blocked_id, **kwargs):

        if len(request.data) != 1:
            return HttpResponseBadRequest()

        with open(PATH, 'r') as fw_json:
            data = json.load(fw_json)
            id_found = False
            try:
                for rule in data['blacklist']:
                    if rule['id'] == int(blocked_id):
                        rule['reason'] = request.data['ruleReason']
                        id_found = True
                        break
            except KeyError as e:
                return HttpResponseNotFound(e)
            if not id_found:
                return HttpResponseNotFound(f"ID {blocked_id} not found in blocked list")
        with open(PATH, 'w') as fw_json:
            json.dump(data, fw_json)
        return Response({"ruleReason": rule['reason']})


class FwBlockedIp(APIView):
    """
    [GET] /firewall/{blockedIp}

    Get all rules with specified blockedIp on firewall

    [PUT] /firewall/{blockedIp}

    Change the reason for all rules with specified IP

    [DELETE] /firewall/{blockedIp}

    Delete all rules for IP
    """

    def get(self, request, blocked_ip, **kwargs):
        with open(PATH, 'r') as fw_json:
            data = json.load(fw_json)
            for rule in data['blacklist']:
                try:
                    if rule['ip'] == blocked_ip:
                        return Response(rule)
                except KeyError as e:
                    return HttpResponseBadRequest(e)

            return HttpResponseNotFound(f"IP {blocked_ip} not found in blocked IPs")

    def put(self, request, blocked_ip, **kwargs):

        if len(request.data) != 1:
            return HttpResponseBadRequest()

        with open(PATH, 'r') as fw_json:
            data = json.load(fw_json)
            ip_found = False
            try:
                for rule in data['blacklist']:
                    if rule['ip'] == blocked_ip:
                        rule['reason'] = request.data['ruleReason']
                        ip_found = True
                        break
            except KeyError as e:
                return HttpResponseNotFound(e)
            if not ip_found:
                return HttpResponseNotFound(f"IP {blocked_ip} not found in blocked IPs")
        with open(PATH, 'w') as fw_json:
            json.dump(data, fw_json)
        return Response(rule)

    def delete(self, request, blocked_ip, **kwargs):
        with open(PATH, 'r') as fw_json:
            data = json.load(fw_json)
            ip_found = False
            try:
                for rule in data['blacklist']:
                    if rule['ip'] == blocked_ip:
                        data['blacklist'].remove(rule)
                        ip_found = True
                        break
            except KeyError as e:
                return HttpResponseBadRequest(e)
            if not ip_found:
                return HttpResponseNotFound(f"IP {blocked_ip} not found in blocked IPs")
        with open(PATH, 'w') as fw_json:
            json.dump(data, fw_json)

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


def check_id(data, new_id):
    for rule in data['blacklist']:
        if rule['id'] == new_id:
            return True
    return False


def check_ip(data, ip):
    for rule in data['blacklist']:
        if rule['ip'] == ip:
            return True
    return False