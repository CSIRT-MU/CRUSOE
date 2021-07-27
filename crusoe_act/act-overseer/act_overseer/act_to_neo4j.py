#!/usr/bin/env python3

import requests
import structlog
import pkg_resources
from requests.auth import HTTPBasicAuth
from datetime import datetime

# Calls all wrappers and updates their health_check and capacities in the database.


def filename(name):
    """ Obtain filepath for the resource.

    :param name: Path to file.
    """
    return pkg_resources.resource_filename(__name__, name)


def get_ip_and_port(pao, wrappers):
    """ This function obtains ip and port of given pao wrapper from list of wrappers.

    :param pao: Given unit of active defense.
    :param wrappers: List of wrappers.
    :return: ip and port to access the wrapper of given 'pao'.
    """
    ip = ''
    port = ''
    for wrapper in wrappers['paos']:
        if wrapper['pao'] == pao:
            ip = wrapper['ip']
            port = wrapper['port']
            break
    return ip, port


def get_paos(user, passwd, server_url, logger):
    """ This function calls REST API of the crusoe server and gets json of units of active defense.

    :param user: User for authentication.
    :param passwd: Password for authentication.
    :param logger: Log file.
    :param server_url: URL of the server with running database.
    :return: Json containing all units of active defense.
    """
    try:
        wrapper_ip_port_get = requests.get(f'{server_url}/rest/act/paos',
                                           auth=HTTPBasicAuth(user, passwd),
                                           verify=filename('data/cert_file.crt'))
        return wrapper_ip_port_get.json()
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Can't connect to database REST API. {e}")


def update_last_contact(pao, user, passwd, server_url, logger):
    """ This function calls REST API of the crusoe server and updates the lastContact attribute in neo4j db.

    :param pao: Name of the unit of active defense.
    :param user: User for authentication.
    :param passwd: Password for authentication.
    :param server_url: URL of the server with running database.
    :param logger: Log file.
    :return: Object of type Response.
    """
    try:
        time = datetime.utcnow().isoformat() + 'Z'
        return requests.post(f'{server_url}/rest/act/{pao}/liveness',
                             json={'lastContact': time},
                             auth=HTTPBasicAuth(user, passwd),
                             verify=filename('data/cert_file.crt'))
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Can't connect to database REST API. {e}")


def check_and_update(pao, user, passwd, server_url, logger):
    """ This function checks and updates liveness of given unit of active defense.

    It checks the liveness using corresponding API wrapper for given unit of active defense.
    Then updates the information in neo4j database.

    :param pao: Unit of active defense.
    :param user: User for authentication.
    :param passwd: Password for authentication.
    :param server_url: URL of the server with running database.
    :param logger: In advance specified log file.
    """
    count = 0
    logger.info(f"Getting {pao} wrapper IP and PORT from neo4j db.")
    ip, port = get_ip_and_port(pao, get_paos(user, passwd, server_url, logger))
    if ip == '' or port == '':
        logger.error(f"IP or port couldn't have been obtained from the database for {pao} ip: {ip} port: {port}")
        return count
    try:
        logger.info(f"Getting health from {pao} wrapper.")
        health_get = requests.get(f'http://{ip}:{port}/{pao}/health')
        if health_get.ok:
            logger.info(f"Updating last contact for {pao}.")
            health_post = update_last_contact(pao, user, passwd, server_url, logger)
            if health_post.ok:
                logger.info(f"{pao} liveness updated successfully.")
                count += 1
            else:
                logger.error(f"Failed to update data in neo4j db for {pao} wrapper.")
        else:
            logger.warning(f"Health check of {pao} wrapper failed")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Can't connect to {pao} wrapper. {e}")
    return count


def update_capacity(pao, user, passwd, capacity_type, capacity_value, server_url, logger):
    """ This function calls REST API of crusoe server and updates certain capacities.

    :param pao: Unit of active defense.
    :param user: User for authentication.
    :param passwd: Password for authentication.
    :param capacity_type: One of 'maxCapacity', 'usedCapacity', 'freeCapacity'.
    :param capacity_value: Value assigned to key 'capacity_type'.
    :param logger: Log file.
    :param server_url: URL of the server with running database.
    :return: Object of type Response.
    """
    try:
        return requests.post(f'{server_url}/rest/act/{pao}/{capacity_type}',
                             json={capacity_type: capacity_value},
                             auth=HTTPBasicAuth(user, passwd),
                             verify=filename('data/cert_file.crt'))
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Can't connect to database REST API. {e}")


def retrieve_and_update_capacity(pao, user, passwd, server_url, logger):
    """ This function retrieves capacities of given unit of active defense and updates them in the neo4j database.

    It's using REST API on the crusoe server to access the neo4j database.
    Wrapper IP and PORT are obtained from the database. Its location is not limited to the server.

    :param pao: Unit of active defense.
    :param user: User for authentication.
    :param passwd: Password for authentication.
    :param server_url: URL of the server with running database.
    :param logger: In advance specified log file.
    """
    count = 0
    logger.info(f"Getting {pao} wrapper IP and PORT from neo4j db.")
    ip, port = get_ip_and_port(pao, get_paos(user, passwd, server_url, logger))
    if ip == '' or port == '':
        logger.error(f"IP or port couldn't have been obtained from the database for {pao} ip: {ip} port: {port}")
        return count
    try:
        capacity_get = requests.get(f'http://{ip}:{port}/{pao}/capacity')
        if capacity_get.ok:
            capacity_json = capacity_get.json()
            # for each type of capacity update its value to the neo4j database
            for capacity_type in ["maxCapacity", "usedCapacity", "freeCapacity"]:
                logger.info(f"Updating {capacity_type} for {pao}.")
                capacity_post = update_capacity(pao, user, passwd, capacity_type, capacity_json[capacity_type], 
                                                server_url, logger)
                if capacity_post.ok:
                    logger.info(f"{pao} {capacity_type} updated successfully.")
                    count += 1
                else:
                    logger.error(f"Failed to send data to neo4j db - {pao} wrapper. Trying to send {capacity_type}")
        else:
            logger.warning(f"Updating capacities for {pao} failed.")
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Can't connect to {pao} wrapper. {e}")
    return count


def update_db(user, passwd, server_url, logger=structlog.get_logger()):
    """ Main function updates liveness and capacities for all units of active defense.

    :param user: User for authentication to access the database REST API.
    :param passwd: Password for authentication to access the database REST API.
    :param server_url: URL of the server with running database.
    :param logger: In advance specified log file.
    """
    # obtain only the paos which are present in the database
    paos = [pao["pao"] for pao in get_paos(user, passwd, server_url, logger)['paos']]
    expected_liveness = len(paos)
    expected_capacities = len(paos)
    for pao in paos:
        logger.info(f"Processing liveness of {pao}.")
        count_liveness = check_and_update(pao, user, passwd, server_url, logger)
        if count_liveness != 1:
            expected_liveness -= 1
        logger.info(f"Processing capacities of {pao}.")
        count_capacities = retrieve_and_update_capacity(pao, user, passwd, server_url, logger)
        if count_capacities != 3:
            expected_capacities -= 1
    return f"{expected_liveness}/{len(paos)} wrappers successfully updated liveness. " \
           f"{expected_capacities}/{len(paos)} wrappers successfully updated capacities."
