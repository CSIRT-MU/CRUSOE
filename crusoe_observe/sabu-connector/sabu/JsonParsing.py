#!/usr/bin/env python3

import json
import os
import re
import structlog
from datetime import datetime
from time import time, sleep

from neo4jclient.SabuConnectorClient import SabuConnectorClient


class WardenException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def warden_is_running(path_to_warden_filer_receiver, logger):
    """
    Checks if warden is running.
    :return: Empty string if there's no problem, otherwise returns a message if function had to restart warden.
    """
    if (os.system(path_to_warden_filer_receiver + ' status')) != 0:
        os.system(path_to_warden_filer_receiver + ' start')
        sleep(2)
        if (os.system(path_to_warden_filer_receiver + ' status')) != 0:
            logger.error("Warden is not running and can't be started. Resolve immediately.")
            raise WardenException('Warden error!')
        logger.info("Warden was not running but was restarted successfully.")
        return 'Warden was not running '
    return ''


def dump_data_to_json_if_ref_key(path_to_json, data):
    """
    Adds data to json.
    :param path_to_json: path to json
    :param data: data to be added
    """
    with open(path_to_json + 'sabu_ref_key.json', 'w') as json_file:
        json.dump(data, json_file)


def dump_data_to_json_if_not_ref_key(path_to_json, data):
    """
    Adds data to json if ref key was not found.
    :param path_to_json: path to json
    :param data: data to be added
    """
    with open(path_to_json + 'sabu_not_ref.json', 'w') as json_file:
        json.dump(data, json_file)


def detect_time_valid(detect_time):
    """
    Inspired by this answer to the problem https://stackoverflow.com/a/61569783.
    Checks, if detect_time of a message is in valid format ISO 8601.
    :param detect_time: Datetime to be checked.
    :return: True if 'detect_time' satisfies the format, False otherwise.
    """
    try:
        datetime.fromisoformat(detect_time)
    except ValueError:
        try:
            datetime.fromisoformat(detect_time.replace('Z', '+00:00'))
        except ValueError:
            return False
        return True
    return True


def parse(directory, passwd, regex, path_to_warden_filer_receiver, path_to_neo4j, logger=structlog.get_logger()):
    """
    Main function parsing IDEA files coming from warden.
    :param: directory - directory where IDEA messages are received (usually ...warden/incoming)
    :param: passwd - password for neo4j database
    :param: regex - regular expression selecting only IPs in range of Masaryk university.
    :param: path_to_warden_filer_receiver Path to warden filer receiver
    :param: path_to_neo4j Path where json will be created
    :return: warden message and number of vulnerabilities found in last 5 minutes
    """
    warden_message = warden_is_running(path_to_warden_filer_receiver, logger)
    client = SabuConnectorClient(password=passwd)
    vulnerable = 0
    final_json_if_ref_key = {'detection_system': "Warden", 'results': []}
    final_json_if_not_ref_key = {'detection_system': "Warden", 'results': []}

    if not os.listdir(directory):  # if directory is empty
        logger.info("Nothing to parse")
    t1 = time()
    for json_file in os.listdir(directory):
        with open(directory + json_file, "r") as source_file:
            read_file = source_file.read()
            match = re.search(regex, read_file)
            if match is None:
                # Received a message, but the IPv4 doesn't match MUNI network.
                os.remove(directory + json_file)
                continue
            try:
                logger.info(f"Parsing the message: {json_file}")
                data = json.loads(read_file)
                detect_time = data['DetectTime']
                # In case of invalid time format, i.e. without 'T' as tenth character, we squeeze the 'T' in.
                detect_time = detect_time.replace(' ', 'T')
                if not detect_time_valid(detect_time):
                    logger.error(f"FAILED (wrong date format): {detect_time}")
                    # Move invalid message to errors folder.
                    os.replace(directory + json_file, directory + "../errors/" + json_file)
                try:
                    # This block satisfies parsing the IDEA message example on https://idea.cesnet.cz/en/index
                    # which is, however, never sent by warden. Most common type of messages are without
                    # the 'Ref' key.
                    cve_id = data['Ref'][0][4:]
                    if 'IP4' in data['Target'][1]:
                        ip_target = data['Target'][1]['IP4'][0]
                    else:
                        ip_target = data['Target'][1]['IP6'][0]
                    final_json_if_ref_key['results'].append({'cve_id': cve_id, 'ip': ip_target,
                                                             'detection_time': detect_time})
                    logger.info(f"Message info: {cve_id} on {ip_target}")
                    vulnerable += 1
                except (KeyError, IndexError):
                    vulnerability = data['Category']
                    # The 'Note' key carries a more detailed description of a message than 'Description', however
                    # 'Note' key is not always present, however one of these keys is.
                    if 'Note' in data:
                        description = data['Note']
                    else:
                        description = data['Description']
                    if 'IP4' in data['Source'][0]:
                        ip_source = data['Source'][0]['IP4'][0]
                    else:
                        if 'IP6' in data['Source'][0]:
                            ip_source = data['Source'][0]['IP6'][0]
                        else:
                            logger.error("There was no source IP provided. Moving the message to errors.")
                            os.replace(directory + json_file, directory + "../errors/" + json_file)

                    final_json_if_not_ref_key['results'].append({'description': description,
                                                                 'vulnerability': vulnerability,
                                                                 'ip': ip_source, 'detection_time': detect_time})
                    logger.info(f"Message info: vulnerability = {vulnerability}, ip4 = {ip_source}, {description}")
                    vulnerable += 1
            except (json.decoder.JSONDecodeError, KeyError, IndexError):
                logger.error("FAILED (Error while parsing - Incorrect message format)")
                os.replace(directory + json_file, directory + "../errors/" + json_file)
            finally:
                logger.info(f"Removing the message: {json_file}")
                # Try to delete the message. If the message has been moved, do nothing.
                try:
                    os.remove(directory + json_file)
                except OSError:
                    pass
    dump_data_to_json_if_ref_key(path_to_neo4j, final_json_if_ref_key)
    dump_data_to_json_if_not_ref_key(path_to_neo4j, final_json_if_not_ref_key)
    t2 = time()
    python_time = t2 - t1
    logger.info(f"Execution before DB {python_time}.")
    if len(final_json_if_ref_key['results']) > 0:
        client.driver_session_if_ref_key('sabu_ref_key.json')
    if len(final_json_if_not_ref_key['results']) > 0:
        client.driver_session_if_not_ref_key('sabu_not_ref.json')
    t3 = time()
    neo_time = t3 - t2
    logger.info(f"DB execution {neo_time}.")
    return f"{warden_message} {str(vulnerable)} vulnerabilities were detected in last 5 minutes." \
           f"Measurement: python_time = {python_time}, neo_time = {neo_time}."
