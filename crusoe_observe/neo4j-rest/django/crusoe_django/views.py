from neo4jclient.RESTClient import RESTClient
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from configparser import ConfigParser
import json
import re
from neo4j.exceptions import ClientError, DatabaseError, TransientError


def get_password():
    config_parser = ConfigParser()
    config_parser.read("/var/www/django/crusoe_django/conf.ini")
    return config_parser['dashboard_rest']['neo4j_password']


client = RESTClient(password=get_password())
LIMIT = 100
OFFSET = 100


def get_limit(request):
    limit = request.GET.get('limit')
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = LIMIT
    return limit


"---------------------------------------------PAO VIEWS----------------------------------------------------------------"


@api_view(['POST'])
def init_pao(request):
    """
    Initialize PAO nodes view.

    :param request: POST request
    :return: HTTP response
    """
    if request.method == 'POST':
        properties = request.data
        data = json.dumps(properties)
        try:
            # reinitialize paos
            client.delete_pao()
            return Response(client.create_pao(data))
        except (ClientError, TransientError, DatabaseError) as e:
            return Response("Exception on neo4j side, pao initialization failed. " + str(e),
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def pao(request):
    """
    Get PAO nodes view.

    :param request: GET request
    :return: HTTP response
    """
    limit = get_limit(request)
    return Response(client.get_all_paos(limit))


@api_view(['GET', 'POST'])
def pao_last_contact(request, pao_name):
    """
    Get/Post information about time of last contact of PAO node view.

    :param request: POST/GET request
    :param pao_name: Name of PAO node
    :return: HTTP response
    """
    if request.method == 'GET':
        return Response(client.get_last_contact_pao(pao_name))
    elif request.method == 'POST':
        properties = request.data
        data = json.loads(json.dumps(properties))
        try:
            return Response(client.set_last_contact_pao(pao_name, data["lastContact"]))
        except (ClientError, TransientError, DatabaseError) as e:
            return Response("Exception on neo4j side, set operation failed. " + str(e),
                            status=status.HTTP_400_BAD_REQUEST)
        except (KeyError, TypeError) as e:
            return Response("Invalid json format, expected " + str(e),
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def pao_max_capacity(request, pao_name):
    """
    GET/POST information about max capacity of PAO node view.

    :param request: GET/POST request
    :param pao_name: Name of PAO node
    :return: HTTP response
    """
    if request.method == 'GET':
        return Response(client.get_max_capacity_pao(pao_name))
    elif request.method == 'POST':
        properties = request.data
        data = json.loads(json.dumps(properties))
        try:
            return Response(client.set_max_capacity_pao(pao_name, data["maxCapacity"]))
        except (ClientError, TransientError, DatabaseError) as e:
            return Response("Exception on neo4j side, set operation failed. " + str(e),
                            status=status.HTTP_400_BAD_REQUEST)
        except (KeyError, TypeError) as e:
            return Response("Invalid json format, expected " + str(e),
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def pao_used_capacity(request, pao_name):
    """
    GET/POST information about used capacity of PAO node view.

    :param request: GET/POST request
    :param pao_name: Name of PAO node
    :return: HTTP response
    """
    if request.method == 'GET':
        return Response(client.get_used_capacity_pao(pao_name))
    elif request.method == 'POST':
        properties = request.data
        data = json.loads(json.dumps(properties))
        try:
            return Response(client.set_used_capacity_pao(pao_name, data["usedCapacity"]))
        except (ClientError, TransientError, DatabaseError) as e:
            return Response("Exception on neo4j side, set operation failed. " + str(e),
                            status=status.HTTP_400_BAD_REQUEST)
        except (KeyError, TypeError) as e:
            return Response("Invalid json format, expected " + str(e),
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
def pao_free_capacity(request, pao_name):
    """
    GET/POST information about free capacity of PAO node view.

    :param request: GET/POST request
    :param pao_name: Name of PAO node
    :return: HTTP response
    """
    if request.method == 'GET':
        return Response(client.get_free_capacity_pao(pao_name))
    elif request.method == 'POST':
        properties = request.data
        data = json.loads(json.dumps(properties))
        try:
            return Response(client.set_free_capacity_pao(pao_name, data["freeCapacity"]))
        except (ClientError, TransientError, DatabaseError) as e:
            return Response("Exception on neo4j side, set operation failed. " + str(e),
                            status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return Response("Invalid json format, expected " + str(e),
                            status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def pao_status(request, pao_name):
    """
    GET information about current pao status.

    :param request: GET request
    :param pao_name: Name of PAO node
    :return: HTTP response
    """
    if request.method == 'GET':
        liveliness = client.get_liveliness_status_pao(pao_name)
        capacity = client.get_capacity_status_pao(pao_name)
        result = {"status_green": "", "status_yellow": "", "status_red": ""}

        # green handling
        if liveliness.startswith("OK") and capacity.startswith("OK"):
            result['status_green'] = "OK"
        # yellow handling
        if capacity.startswith("Capacity 90"):
            result['status_yellow'] = capacity
        if liveliness.startswith("Last"):
            if result['status_yellow'] != "":
                result['status_yellow'] += f", {liveliness}"
            else:
                result['status_yellow'] = liveliness
        # red handling
        if capacity.startswith("Capacity full"):
            result['status_red'] = capacity
        if liveliness.startswith("Unreachable"):
            if result['status_red'] != "":
                result['status_red'] += f", {liveliness}"
            else:
                result['status_red'] = liveliness

        return Response(result)


"___________________________________________ORANGE LAYER_______________________________________________________________"


@api_view(['GET'])
def events(request):
    """
    GET information about events view.

    :param request: GET request
    :return: HTTP response
    """
    limit = get_limit(request)
    return Response(client.get_all_events(limit))


@api_view(['GET'])
def events_by_date(request, date):
    """
    GET events from specific time period view.

    :param request: GET request
    :param date: ISO date
    :return: HTTP response
    """
    date = re.sub('/', '-', date)
    limit = get_limit(request)
    return Response(client.get_events_by_date(date, limit))


@api_view(['GET'])
def events_after_date(request, date):
    """
    GET events after specific time view.

    :param request: GET request
    :param date: ISO date
    :return: HTTP response
    """
    date = re.sub('/', '-', date)
    limit = get_limit(request)
    return Response(client.get_events_after_date(date, limit))


"________________________________________________RED & BLUE LAYER_____________________________________________________"


@api_view(['GET', 'POST'])
def mission(request):
    """
    GET/POST information about missions view.

    :param request: GET/POST request
    :return: HTTP response
    """
    if request.method == 'GET':
        limit = get_limit(request)
        return Response(client.get_all_mission(limit))
    elif request.method == 'POST':
        properties = request.data
        try:
            data = json.dumps(properties)
            return Response(client.create_missions_and_components_string(data))
        except (ClientError, TransientError, DatabaseError) as e:
            return Response("Exception on neo4j side, set operation failed. " + str(e),
                            status=status.HTTP_400_BAD_REQUEST)
        except (KeyError, TypeError) as e:
            return Response("Structured data was not provided or are incorrect.", status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'DELETE'])
def mission_details(request, name):
    """
    GET information about specified mission / DELETE specified mission.

    :param request: GET/DELETE request
    :param name: name of mission
    :return: HTTP response
    """
    if not client.mission_exists(name):
        return Response("Mission does not exist", status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'GET':
        return Response(client.get_mission_details(name))
    if request.method == 'DELETE':
        return Response(client.delete_mission(name))


@api_view(['GET'])
def mission_configurations(request, name):
    """
    GET list of mission's configurations, their evaluation and timestamp of the evaluation.

    :param request: GET request
    :param name: name of mission
    :return: HTTP response
    """
    return Response(client.get_mission_configurations(name))


@api_view(['GET'])
def mission_hosts(request, name):
    """
    GET hosts from mission's constrained AND/OR tree, their IPs and IDs.

    :param request: GET request
    :param name: name of mission
    :return: HTTP response
    """
    return Response(client.get_mission_hosts(name))


@api_view(['GET'])
def configuration(request, name, config_id):
    """
    GET hosts which appear in the mission's configuration, their IPs and evaluation.

    :param request: GET request
    :param name: name of mission
    :param config_id: ID of configuration
    :return: HTTP response
    """
    return Response(client.get_configuration(name, int(config_id)))


@api_view(['GET'])
def hosts_for_all_missions(request):
    """
    GET hosts which appear in any of missions that are in the database, together with IPs and
    the worst-case evaluation of hosts in one of missions.

    :param request: GET request
    :return: HTTP response
    """
    return Response(client.get_missions_hosts_evaluation())


"_____________________________________________PURPLE LAYER____________________________________________________________"


@api_view(['GET'])
def cve(request):
    """
    GET CVEs with specified limit.

    :param request: GET request
    :return: HTTP response
    """
    limit = get_limit(request)
    return Response(client.get_all_cve(limit))


@api_view(['GET'])
def cve_details(request, cve_id):
    """
    GET properties of CVE specified by its ID.

    :param request: GET request
    :param cve_id: CVE ID
    :return: HTTP response
    """
    if not client.cve_exists(cve_id):
        return Response("CVE does not exist.", status=status.HTTP_400_BAD_REQUEST)
    return Response(client.get_cve(cve_id))


@api_view(['GET'])
def cve_ips(request, cve_id):
    """
    GET IP adresses of machines on which specified CVE is present.

    :param request: GET request
    :param cve_id: CVE ID
    :return: HTTP response
    """
    if not client.cve_exists(cve_id):
        return Response("CVE does not exists.", status=status.HTTP_400_BAD_REQUEST)
    limit = get_limit(request)
    return Response(client.get_all_ip_with_cve(cve_id, limit))


"____________________________________________GREEN LAYER__________________________________________________________"


@api_view(['GET'])
def software(request):
    """
    GET list of :SoftwareVersion nodes up to limit.

    :param request: GET request
    :return: HTTP response
    """
    limit = get_limit(request)
    return Response(client.get_software_resources(limit))


@api_view(['GET'])
def software_ips(request, name):
    """
    GET IPS for nodes of :SoftwareVersion type.

    :param request: GET request
    :param name: abbreviated CPE in the form of <vendor>:<product>:<version>
    :return: HTTP response
    """
    if not client.software_exists(name):
        return Response("Software does not exists", status=status.HTTP_400_BAD_REQUEST)
    limit = get_limit(request)
    return Response(client.get_software_ips(name, limit))


@api_view(['GET'])
def services(request):
    """
    GET services from database together with protocol and port up to limit.

    :param request: GET request
    :return: HTTP response
    """
    limit = get_limit(request)
    return Response(client.get_network_services(limit))


@api_view(['GET'])
def service_details(request, name):
    """
    GET details for service specified by its name.

    :param request: GET request
    :param name: name of service, e.g., SSH
    :return: HTTP response
    """
    if not client.network_service_exists(name):
        return Response("Network service does not exists", status=status.HTTP_400_BAD_REQUEST)
    return Response(client.get_network_service_details(name))


# TODO
@api_view(['GET'])
def service_ips(request, name):
    """
    GET IP addresses for specified service.

    :param request: GET request
    :param name: name of service, e.g., SSH
    :return: HTTP response
    """
    if not client.network_service_exists(name):
        return Response("Network service does not exists", status=status.HTTP_400_BAD_REQUEST)
    limit = get_limit(request)
    return Response(client.get_network_service_ips(name, limit))


"______________________________________YELLOW LAYER_____________________________________________________"


@api_view(['GET'])
def org_units(request):
    """
    GET organization units from database.

    :param request: GET request
    :return: HTTP response
    """
    limit = get_limit(request)
    return Response(client.get_all_organization_units(limit))


@api_view(['GET'])
def org_unit_subnets(request, name):
    """
    GET network subnets for specified organization unit.

    :param request: GET request
    :param name: name of an organization unit
    :return: HTTP response
    """
    if not client.organization_unit_exists(name):
        return Response("Organization unit does not exist.", status=status.HTTP_400_BAD_REQUEST)
    limit = get_limit(request)
    return Response(client.get_organization_unit_subnets(name, limit))


"______________________________________LIGHT-BLUE LAYER_____________________________________________________"


@api_view(['GET'])
def ip(request):
    """
    GET IPs in database up to limit.

    :param request: GET request
    :return: HTTP response
    """
    limit = get_limit(request)
    return Response(client.get_all_ips(limit))


@api_view(['GET'])
def ip_details(request, address):
    """
    GET details for specified IP (its subnet, organization unit, domain name, and contact).

    :param request: GET request
    :param address: IP address
    :return: HTTP response
    """
    if not client.ip_exists(address):
        return Response("IP does not exists", status=status.HTTP_400_BAD_REQUEST)
    return Response(client.get_ip_details(address))


@api_view(['GET'])
def ip_events(request, address):
    """
    GET security events related to the specified IP.

    :param request: GET request
    :param address: IP address
    :return: HTTP response
    """
    if not client.ip_exists(address):
        return Response("IP does not exists", status=status.HTTP_400_BAD_REQUEST)
    limit = get_limit(request)
    return Response(client.get_ip_sec_events(address, limit))


@api_view(['GET'])
def ip_events_latest(request, address):
    """
    GET latest security events for specified IP up to limit.

    :param request: GET request
    :param address: IP address
    :return: HTTP response
    """
    if not client.ip_exists(address):
        return Response("IP does not exists", status=status.HTTP_400_BAD_REQUEST)
    limit = get_limit(request)
    return Response(client.get_ip_active_events(address, limit))


@api_view(['GET'])
def ip_events_date(request, address, date):
    """
    GET all security events which happened on specified date and are related to specified IP.

    :param request: GET request
    :param address: IP address
    :param date: date in the form of <year>/<month>/<day>, day and month are not required
    :return: HTTP response
    """
    date = re.sub('/', '-', date)
    if not client.ip_exists(address):
        return Response("IP does not exists", status=status.HTTP_400_BAD_REQUEST)
    limit = get_limit(request)
    return Response(client.get_ip_date_events(address, date, limit))


@api_view(['GET'])
def ip_services(request, address):
    """
    GET all network service running on a specified IP up to limit.

    :param request: GET request
    :param address: IP address
    :return: HTTP response
    """
    if not client.ip_exists(address):
        return Response("IP does not exists", status=status.HTTP_400_BAD_REQUEST)
    limit = get_limit(request)
    return Response(client.get_ip_services(address, limit))


@api_view(['GET'])
def ip_software(request, address):
    """
    GET all :SoftwareVersion nodes running on specified IP up to limit.

    :param request: GET request
    :param address: IP address
    :return: HTTP response
    """
    if not client.ip_exists(address):
        return Response("IP does not exists", status=status.HTTP_400_BAD_REQUEST)
    limit = get_limit(request)
    return Response(client.get_ip_software(address, limit))


@api_view(['GET'])
def ip_cve(request, address):
    """
    GET all CVEs running on specified IP up to limit.

    :param request: GET request
    :param address: IP address
    :return: HTTP response
    """
    if not client.ip_exists(address):
        return Response("IP does not exists", status=status.HTTP_400_BAD_REQUEST)
    limit = get_limit(request)
    return Response(client.get_ip_cve(address, limit))


@api_view(['GET'])
def subnet(request):
    """
    GET all subnets from the database up to limit.

    :param request: GET request
    :return: HTTP response
    """
    limit = get_limit(request)
    return Response(client.get_subnets(limit))


@api_view(['GET'])
def subnet_ips(request, subnet):
    """
    GET all IPs in specified subnet up to limit.

    :param request: GET request
    :param subnet: subnet specified using CIDR notation
    :return: HTTP response
    """
    if not client.subnet_exists(subnet):
        return Response("Subnet does not exist.", status=status.HTTP_400_BAD_REQUEST)
    limit = get_limit(request)
    return Response(client.get_subnet_ips(subnet, limit))


@api_view(['GET'])
def subnet_details(request, subnet):
    """
    GET details for specified subnet (e.g., contact and organization).

    :param request: GET request
    :param subnet: subnet specified using CIDR notation
    :return: HTTP response
    """
    if not client.subnet_exists(subnet):
        return Response("Subnet does not exist.", status=status.HTTP_400_BAD_REQUEST)
    limit = get_limit(request)
    return Response(client.get_subnets_details(subnet))
