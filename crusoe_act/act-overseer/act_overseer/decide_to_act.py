import requests
import time
from json import load
from requests.auth import HTTPBasicAuth
from act_overseer.act_to_neo4j import filename, update_db, get_paos, get_ip_and_port


class OverseerException(Exception):
    """ Custom exception to be raised when overseer cannot continue until issue is resolved. """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


"-------------------------------------------Functions for input control in REST API------------------------------------"


def get_missions(user, passw, logger, dashboard_log, server_url):
    """ This function gets all missions using database REST API.

    :param user: Username to access the database REST API.
    :param passw: Password, along with 'user' used to access the database REST API.
    :param logger: Logger object.
    :param dashboard_log: Log messages which will be shown on dashboard.
    :param server_url: URL of the server with running database.
    :return: Upon successful REST API call, returns JSON containing all missions.
    """
    try:
        return requests.get(f"{server_url}/rest/missions",
                            auth=HTTPBasicAuth(user, passw),
                            verify=filename('data/cert_file.crt')).json()
    except requests.exceptions.ConnectionError as e:
        logger.critical(f"Can't connect to database REST API on GET /rest/missions. {e}")
        dashboard_log.append(
            {"message": f"Can't connect to database REST API on /rest/missions.",
             "time": time.time()})
        raise OverseerException(f"Connection to neo4j REST API failed on GET /rest/missions. {e}")


def get_configurations(user, passw, mission, logger, dashboard_log, server_url):
    """ This function obtains all configurations using database REST API for given 'mission'.
    Used to check whether give configuration for a 'mission' is a valid configuration.

    :param user: Username to access the database REST API.
    :param passw: Password, along with 'user' used to access the database REST API.
    :param mission: Mission name to which configurations belong.
    :param logger: Logger object.
    :param dashboard_log: Log messages which will be shown on dashboard.
    :param server_url: URL of the server with running database.
    :return: Upon successful REST API call, returns JSON containing configurations for given mission.
    """
    try:
        return requests.get(f"{server_url}/rest/mission/{mission}/configurations",
                            auth=HTTPBasicAuth(user, passw),
                            verify=filename('data/cert_file.crt')).json()
    except requests.exceptions.ConnectionError as e:
        logger.critical(f"Can't connect to database REST API on /rest/missions/{mission}/configurations. {e}")
        dashboard_log.append(
            {"message": f"Can't connect to database REST API on /rest/missions/{mission}/configurations.",
             "time": time.time()})
        raise OverseerException(f"Connection to neo4j RESTA PI failed on "
                                f"GET /rest/missions/{mission}/configurations. {e}")


"-------------------------------------------Functions for computing blockings------------------------------------------"


def get_fw_ip_and_port(user, passw, logger, server_url):
    """ This function gets ip and port of firewall wrapper

    :param user: Username to access the database REST API.
    :param passw: Password, along with 'user' used to access the database REST API.
    :param logger: Logger object.
    :param server_url: URL of the server with running database.
    :return: String containing IP and PORT in format {ip}:{port}.
    """
    ip, port = get_ip_and_port('firewall', get_paos(user, passw, server_url, logger))
    return f"{ip}:{port}"


def get_hosts(user, passw, logger, dashboard_log, server_url):
    """ This function obtains all hosts using database REST API.

    :param user: Username to access the database REST API.
    :param passw: Password, along with 'user' used to access the database REST API.
    :param logger: Logger object.
    :param dashboard_log: Log messages which will be shown on dashboard.
    :param server_url: URL of the server with running database.
    :return: Upon successful call, returns JSON containing all hosts.
    """
    try:
        return requests.get(f"{server_url}/rest/missions/hosts",
                            auth=HTTPBasicAuth(user, passw),
                            verify=filename('data/cert_file.crt')).json()
    except requests.exceptions.ConnectionError as e:
        logger.critical(f"Can't connect to database REST API on /rest/missions/hosts. {e}")
        dashboard_log.append({"message": f"Can't connect to database REST API on /rest/missions/hosts.",
                              "time": time.time()})
        raise OverseerException(f"Connection to neo4j REST API failed on /rest/missions/hosts. {e}")


def get_important_mission_hosts(user, passw, mission, configuration, logger, dashboard_log, server_url):
    """ This function obtains all important hosts for given mission and its configuration
        using database REST API.

    :param user: Username to access the database REST API.
    :param passw: Password, along with 'user' used to access the database REST API.
    :param mission: Name of the mission.
    :param configuration: Id of the configuration.
    :param logger: Logger object.
    :param dashboard_log: Log messages which will be shown on dashboard.
    :param server_url: URL of the server with running database.
    :return: JSON with important hosts for give mission.
    """
    try:
        return requests.get(f"{server_url}/rest/mission/{mission}/configuration/{configuration}/hosts",
                            auth=HTTPBasicAuth(user, passw),
                            verify=filename('data/cert_file.crt')).json()
    except requests.exceptions.ConnectionError as e:
        logger.critical(f"Can't connect to database REST API on "
                        f"/rest/mission/{mission}/configuration/{configuration}. {e}")
        dashboard_log.append(
            {"message": f"Can't connect to database REST API on /rest/mission/{mission}/configuration/{configuration}.",
             "time": time.time()})
        raise OverseerException(f"Connection to neo4j REST API failed on "
                                f"/rest/mission/{mission}/configuration/{configuration}. {e}")


def potential_blocking(user, passw, missions_and_configurations, logger, dashboard_log, server_url):
    """ This function filters important hosts for given (mission, configuration) pairs from all hosts
        and creates a list of potential blockings.

    :param user: Username to access the database REST API.
    :param passw: Password, along with 'user' used to access the database REST API.
    :param missions_and_configurations: (mission, configuration) pairs obtained from act-overseer REST API.
    :param logger: Logger object.
    :param dashboard_log: Log messages which will be shown on dashboard.
    :param server_url: URL of the server with running database.
    :return: List of potential blockings.
    """
    all_hosts = get_hosts(user, passw, logger, dashboard_log, server_url)
    for mission_and_configuration in missions_and_configurations:
        mission_name = mission_and_configuration['name']
        configuration = mission_and_configuration['config_id']

        mission_conf_hosts = get_important_mission_hosts(user, passw, mission_name, configuration, logger,
                                                         dashboard_log, server_url)
        # all_hosts - mission_conf_hosts using its IP as unique id
        for host in mission_conf_hosts:
            try:
                host_ip = host['host']['ip_address']
            except KeyError as e:
                logger.error(f"{host} is in invalid format: {e}")
                continue
                # error, continue next iteration
            for all_host in all_hosts:
                try:
                    all_host_ip = all_host['host']['ip_address']
                except KeyError as e:
                    logger.error(f"/missions/hosts returns invalid format: {e}")
                    raise KeyError(e)
                    # error, continue next iteration

                if all_host_ip == host_ip:
                    all_hosts.remove(all_host)

    return all_hosts  # potential blockings


def get_firewall_health(logger, dashboard_log, firewall_ip_and_port):
    """ This function calls firewall wrapper and gets its health status.

    :param logger: Logger object.
    :param dashboard_log: Log messages which will be shown on dashboard.
    :param firewall_ip_and_port: URL of firewall wrapper.
    :return: True if firewall is alive, False otherwise.
    """
    try:
        request = requests.get(f"http://{firewall_ip_and_port}/firewall/health")
        if request.ok:
            return True
        else:
            logger.warning(f"Firewall health check failed with code {request.status_code}.")
            dashboard_log.append({"message": f"Firewall health check failed with code {request.status_code}.",
                                  "time": time.time()})
            return False
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Can't connect to firewall wrapper. {e}")
        dashboard_log.append({"message": "Can't connect to firewall wrapper.",
                              "time": time.time()})
        return False


def get_firewall_capacities(logger, dashboard_log, firewall_ip_and_port):
    """ This function calls firewall wrapper and gets its capacities.

    :param logger: Logger object.
    :param dashboard_log: Log messages which will be shown on dashboard.
    :param firewall_ip_and_port: URL of firewall wrapper.
    :return: Json with capacities of the firewall, None if connection failed.
    """
    try:
        request = requests.get(f"http://{firewall_ip_and_port}/firewall/capacity")
        if request.ok:
            return request.json()
        else:
            logger.warning(f"Getting firewall capacities failed with code {request.status_code}")
            dashboard_log.append({"message": f"Getting firewall capacities failed with code {request.status_code}",
                                  "time": time.time()})

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Can't connect to firewall wrapper. {e}")
        dashboard_log.append({"message": "Can't connect to firewall wrapper.",
                              "time": time.time()})


def get_treshold(logger, dashboard_log):
    """ This function gets security_treshold value.

    :param logger: Logger object.
    :param dashboard_log: Log messages which will be shown on dashboard.
    :return: security_treshold value.
    """
    try:
        with open(filename('data/act_overseer_config'), 'r') as config:
            cfg = load(config)
            return cfg['security_treshold']
    except KeyError as e:
        logger.critical(f"'security_treshold' key is missing in config file. {e}")
        dashboard_log.append({"message": "'security_treshold' key is missing in config file",
                              "time": time.time()})
        raise OverseerException(f"'security_treshold' key is missing in config file. {e}")


def remove_less_than_treshold(potential_blockings, logger, dashboard_log):
    """ This function removes hosts with lower than 'treshold' security value from potential blockings list,
        a.k.a creates a new list containing only hosts with security value higher than 'treshold'.

    :param potential_blockings: List of hosts to be blocked.
    :param logger: Logger object.
    :param dashboard_log: Log messages which will be shown on dashboard.
    :return: List of hosts with security value higher than 'treshold'.
    """
    treshold = get_treshold(logger, dashboard_log)
    # create a new list containing all hosts with security value higher than treshold
    # inspired by https://stackoverflow.com/a/1207461
    return [host for host in potential_blockings if not get_average_security_value(host, logger) < treshold]


def get_average_security_value(host, logger):
    """ This function computes average of 3 values in 'host': availability, confidentiality, integrity.

    :param host: Dictionary representing the host.
    :param logger: Logger object.
    :return: Average of the three values.
    """
    try:
        availability = host['host']['avail'] * 100
    except KeyError as e:
        logger.error(f"Availability key is missing. {e}")
        availability = 100
        # Most of these errors really should not happen, especially in this function, missing keys
        # are highly unlikely, but it can happen. Availability, confidentiality and integrity are
        # set to default values, which is only because they might be uninitialised if one of these
        # keys is missing. I suggest to raise KeyError here with message (e), which will give
        # enough information of the problem. Again, just catching the exception to log it, if
        # it decides to happen. Same for others.
    try:
        confidentiality = host['host']['conf'] * 100
    except KeyError as e:
        logger.error(f"Confidentiality key is missing. {e}")
        confidentiality = 100
    try:
        integrity = host['host']['integ'] * 100
    except KeyError as e:
        logger.error(f"Integrity key is missing. {e}")
        integrity = 100
    return (availability + confidentiality + integrity) / 3


def get_blocked_ips(logger, dashboard_log, firewall_ip_and_port):
    """ This function calls firewall wrapper and gets list of blocked IPs.

    :param logger: Logger object.
    :param dashboard_log: Log messages which will be shown on dashboard.
    :param firewall_ip_and_port: URL of firewall wrapper.
    :return: Json with blocked IPs, None if connection fails.
    """
    try:
        request = requests.get(f"http://{firewall_ip_and_port}/firewall/blocked")
        if request.ok:
            return request.json()
        else:
            logger.warning(f"Getting blocked IPs on firewall failed with code {request.status_code}")
            dashboard_log.append({"message": f"Getting blocked IPs on firewall failed with code {request.status_code}",
                                  "time": time.time()})
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Can't connect to firewall wrapper. {e}")
        dashboard_log.append({"message": "Can't connect to firewall wrapper.",
                              "time": time.time()})
        # error, continue program


def is_already_blocked(ip, firewall_ip_and_port):
    """ This function checks if {ip} is already blocked in the firewall.

    :param ip: IP to check.
    :param firewall_ip_and_port: URL of firewall wrapper.
    :return: True if IP if already blocked on the firewall, False otherwise.
    """
    return requests.get(f"http://{firewall_ip_and_port}/firewall/{ip}").ok


def block_ip(ip, logger, dashboard_log, firewall_ip_and_port):
    """ This function blocks given 'ip' using firewall wrapper.

    :param ip: IP to block.
    :param logger: Logger object.
    :param dashboard_log: Log messages which will be shown on dashboard.
    :param firewall_ip_and_port: URL of firewall wrapper.
    """
    if not is_already_blocked(ip, firewall_ip_and_port):
        try:
            data = {
                "ip": ip,
                "port": 0,
                "reason": ""
            }
            request = requests.post(f"http://{firewall_ip_and_port}/firewall/blocked", json=data)
            if not request.ok:
                logger.error(f"Blocking IP {ip} was unsuccessful. Code {request.status_code}")
                dashboard_log.append({"message": f"Blocking IP {ip} was unsuccessful. Code {request.status_code}",
                                      "time": time.time()})
                return False
            return True
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Can't connect to firewall wrapper. {e}")
            dashboard_log.append({"message": f"Can't connect to firewall wrapper.",
                                  "time": time.time()})
            return False
            #  error, continue program


def unblock_ip(ip, logger, dashboard_log, firewall_ip_and_port):
    """ This function unblocks given 'ip' using firewall wrapper.

    :param ip: IP to unblock.
    :param logger: Logger object.
    :param dashboard_log: Log messages which will be shown on dashboard.
    :param firewall_ip_and_port: URL of firewall wrapper.
    """
    try:
        request = requests.delete(f"http://{firewall_ip_and_port}/firewall/{ip}")
        if not request.ok:
            logger.error(f"Unblocking IP {ip} was unsuccessful. Code {request.status_code}")
            dashboard_log.append({"message": f"Unblocking IP {ip} was unsuccessful. Code {request.status_code}",
                                  "time": time.time()})
            return False
        return True
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Can't connect to firewall wrapper. {e}")
        dashboard_log.append({"message": "Can't connect to firewall wrapper.",
                              "time": time.time()})
        return False


def unblock_list(blocked_ips_list, to_block_list):
    """ This function creates list of IPs that are present in the firewall block list, but not in
        the list of new blockings which will be sent to the firewall.

    :param blocked_ips_list: List of blocked IPs.
    :param to_block_list: List of new blockings.
    :return: List of IPs to be unblocked.
    """
    to_be_unblocked_list = []
    for blocked in blocked_ips_list:
        found_ip = False
        blocked_ip = blocked['ip']
        for host in to_block_list:
            if host['host']['ip_address'] == blocked_ip:
                found_ip = True
        # if the blocked_ip was not found in list of blockings, unblock it
        if not found_ip:
            to_be_unblocked_list.append(blocked_ip)
    return to_be_unblocked_list


def block_list(to_block_list, blocked_ips_list):
    """ This function creates list of IPs that are not present in the firewall block-list, but are present
        in the to-block list.

    :param to_block_list: List of IPs to be blocked.
    :param blocked_ips_list: List of blocked IPs.
    :return: List of IPs to be blocked.
    """
    to_be_blocked_list = []
    for host in to_block_list:
        found_ip = False
        host_ip = host['host']['ip_address']
        for blocked in blocked_ips_list:
            if blocked['ip'] == host_ip:
                found_ip = True
        # if we want to block already blocked IP, nothing happens,
        # but if the host IP was not found in blocked IPs, block it
        if not found_ip:
            to_be_blocked_list.append(host_ip)
    return to_be_blocked_list


def can_unblocks_and_blocks_be_performed(blocked_ips, list_of_new_blockings, logger, dashboard_log,
                                         firewall_ip_and_port):
    """ This function decides if firewall freeCapacity is sufficient for performing new blockings.

    :param blocked_ips: List of blocked IPs.
    :param list_of_new_blockings: List of IPs to be blocked.
    :param logger: Logger object.
    :param dashboard_log: Log messages which will be shown on dashboard.
    :param firewall_ip_and_port: URL of firewall wrapper.
    :return: True if freeCapacity after unblocks is sufficient, False otherwise
    """
    if not get_firewall_health(logger, dashboard_log, firewall_ip_and_port):
        return False
    capacities = get_firewall_capacities(logger, dashboard_log, firewall_ip_and_port)
    unblock_length = 0
    block_length = 0
    if blocked_ips:
        unblock_length = len(unblock_list(blocked_ips, list_of_new_blockings))
        block_length = len(block_list(list_of_new_blockings, blocked_ips))
    if capacities['freeCapacity']:
        new_free_capacity = capacities['freeCapacity'] + unblock_length
    else:
        new_free_capacity = block_length
    if new_free_capacity < block_length:
        for host in list_of_new_blockings:
            logger.error(f"{host['host']['ip_address']} was not blocked on firewall: insufficient free capacity.")
            dashboard_log.append(
                {"message": f"{host['host']['ip_address']} was not blocked on firewall: insufficient free capacity.",
                 "time": time.time()})
        # there's not enough space for new blockings
        return False
    return True


def run_decide_to_act(user, passw, missions_and_configurations, logger, dashboard_log, server_url):
    """
    :param user: User for authentication to access the database REST API.
    :param passw: Password for authentication to access the database REST API.
    :param missions_and_configurations: Directly obtained from POST request to
                                        act/protect_missions_assets.
    :param logger: Logger object.
    :param dashboard_log: Log messages which will be shown on dashboard.
    :param server_url: URL of the server with running database.
    :return: String with information how many IPs were unblocked and blocked on the firewall.
    """

    logger.info("Starting module decide_to_act.py.")
    list_of_potential_blockings = potential_blocking(user, passw, missions_and_configurations, logger, dashboard_log,
                                                     server_url)
    list_of_new_blockings = remove_less_than_treshold(list_of_potential_blockings, logger, dashboard_log)
    logger.info("List of new blockings ready.")
    firewall_ip_and_port = get_fw_ip_and_port(user, passw, logger, server_url)
    blocked_ips = get_blocked_ips(logger, dashboard_log, firewall_ip_and_port)

    unblock_count = 0
    block_count = 0
    if can_unblocks_and_blocks_be_performed(blocked_ips, list_of_new_blockings, logger, dashboard_log,
                                            firewall_ip_and_port):
        for ip in unblock_list(blocked_ips, list_of_new_blockings):
            logger.info(f"Unblocking {ip} on firewall")
            if unblock_ip(ip, logger, dashboard_log, firewall_ip_and_port):
                dashboard_log.append({"message": f"IP {ip} unblocked",
                                      "time": time.time()})
                unblock_count += 1
        for ip in block_list(list_of_new_blockings, blocked_ips):
            logger.info(f"Blocking {ip} on firewall")
            if block_ip(ip, logger, dashboard_log, firewall_ip_and_port):
                dashboard_log.append({"message": f"IP {ip} blocked",
                                      "time": time.time()})
                block_count += 1
        logger.info("Updating PAO parameters in neo4j database")
        update_db(user, passw, server_url, logger)
    dashboard_log.append(
        {"message": f"Applying configurations finished: {unblock_count} IPs were unblocked on the firewall, "
                    f"{block_count} IPs were blocked", "time": time.time()})
    return f"{unblock_count} IPs were unblocked on the firewall, {block_count} IPs were blocked"
