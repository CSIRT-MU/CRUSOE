from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound
from collections import deque

import json
import logging
import time

from act_overseer import decide_to_act
from act_overseer.act_to_neo4j import filename

DASHBOARD_LOG = deque(maxlen=100)


class ProtectMissionsAssets(APIView):
    """
    [POST] /act/protect_missions_assets

    Receives json with the list of the mission-configuration pairs and checks if all missions present
    in the file are correct.
    """

    def post(self, request, **kwargs):
        """
        400 - Invalid request.
        403 - Mission list does not match the list in neo4j.
        404 - Configuration ID does not exist.
        200 - OK. Applying configurations.
        """
        user, passw, log_path, server_url = parse_config()
        rest_api_logger = setup_logger('rest_api_logger', f'{log_path}act_overseer_rest_api.log')
        decide_to_act_logger = setup_logger('decide_to_act', f'{log_path}act_decide_to_act.log')
        missions = decide_to_act.get_missions(user, passw, decide_to_act_logger, DASHBOARD_LOG, server_url)
        # check all mission names and configurations
        rest_api_logger.info("Checking missions names.")
        num_of_missions = 0
        # if there a problem on the next line with request.data, this might means that request.data is not a json
        # check if the REST API isn't receiving form-data instead of json type.
        for data in request.data:
            mission, configuration = check_mission_name(data)
            configurations = decide_to_act.get_configurations(user, passw, mission, decide_to_act_logger, DASHBOARD_LOG,
                                                              server_url)
            found_mission = False
            found_configuration = False
            for miss in missions:
                if mission == miss['name']:
                    num_of_missions += 1
                    found_mission = True
            rest_api_logger.info(f"Checking configurations for mission {mission}.")
            for config in configurations:
                if configuration == config['configuration']['config_id']:
                    found_configuration = True
            if not found_mission:
                rest_api_logger.error(f"'{data['name']}' is invalid mission name.")
                return HttpResponseForbidden(f"'{data['name']}' is invalid mission name.")
            if not found_configuration:
                rest_api_logger.error(f"'{data['config_id']}' is invalid configuration"
                                      f" for mission {data['name']}.")
                return HttpResponseNotFound(f"'{data['config_id']}' is invalid configuration"
                                            f" for mission {data['name']}.")

        if num_of_missions != len(missions):
            rest_api_logger.error(f"Not all missions are listed, only"
                                  f" {num_of_missions}/{len(missions)}")
            return HttpResponseBadRequest(f"Not all missions are listed, only"
                                          f" {num_of_missions}/{len(missions)}")

        rest_api_logger.info("Calling module decide_to_act.py.")
        for data in request.data:
            DASHBOARD_LOG.append({"message": f"Applying configuration with ID {data['config_id']} "
                                             f"for mission {data['name']}",
                                  "time": time.time()})

        return Response(decide_to_act.run_decide_to_act(user, passw, request.data, decide_to_act_logger,
                                                        DASHBOARD_LOG, server_url))


class SecurityTreshold(APIView):
    """
    [GET] /act/treshold

    Returns the current security treshold, devices with higher rating will be blocked.

    [PUT] /act/treshold

    Changes current security treshold to a new one.
    """

    def get(self, request, **kwargs):
        with open(filename('data/act_overseer_config'), 'r') as treshold_json:
            data = json.load(treshold_json)
            security_treshold = data['security_treshold']
        return Response({"security_treshold": security_treshold})

    def put(self, request, **kwargs):
        """ Obtains new security treshold value from the dashboard and
        changes the treshold value in json configuration file.

        400 - Treshold value is invalid.
        200 - OK. Value changed.
        """
        with open(filename('data/act_overseer_config'), 'r') as treshold_json:
            _, _, log_path, _ = parse_config()
            treshold_logger = setup_logger('treshold_logger', f'{log_path}act_overseer_rest_api.log')
            data = json.load(treshold_json)
            from_bytes_to_dict = request.data
            new_security_treshold_value = from_bytes_to_dict['security_treshold']
            # check if the value is valid
            if new_security_treshold_value < 0 or new_security_treshold_value > 100:
                treshold_logger.error(f"{new_security_treshold_value} is invalid value"
                                      f" (its value has to be in range <0, 100>)")
                return HttpResponseBadRequest(f"Security treshold value ({new_security_treshold_value}) is invalid.")
            old_value = data['security_treshold']
            if new_security_treshold_value == old_value:
                return Response("Security treshold value unchanged (same value)")
            data['security_treshold'] = new_security_treshold_value
        with open(filename('data/act_overseer_config'), 'w') as treshold_update:
            # write changes to json file
            json.dump(data, treshold_update)
        treshold_logger.info(f"Security treshold value changed: {old_value} -> {new_security_treshold_value}")
        DASHBOARD_LOG.append(
            {"message": f"Security treshold value changed: {old_value} -> {new_security_treshold_value}",
             "time": time.time()})
        return Response("Security treshold value changed")


class Log(APIView):
    """
    [GET] /act/log

    Returns response with list of log messages.
    """

    def get(self, request, **kwargs):
        return Response(list(DASHBOARD_LOG))


def parse_config():
    """ This helper function parses the config in /data/act_overseer_config

    :return: tuple (user, pass, log_path) obtained from the config.
    """
    with open(filename('data/act_overseer_config'), 'r') as config:
        cfg = json.load(config)
        user = cfg['user']
        passw = cfg['password']
        log_path = cfg['log_path']
        server_url = cfg['server_url']
    return user, passw, log_path, server_url


def check_mission_name(data):
    """ This helper function checks if mission names are correct.

    :param data: data obtained from dashboard
    :return: tuple (mission, configuration)
    """
    if 'name' in data:
        mission = data['name']
    else:
        logging.error("Invalid request, 'name' key is missing.")
        return HttpResponseBadRequest("Invalid request, 'name' key is missing.")
    if 'config_id' in data:
        configuration = data['config_id']
    else:
        logging.error("Invalid request, 'config_id' key is missing.")
        return HttpResponseBadRequest("Invalid request, 'config_id' key is missing.")
    return mission, configuration


# inspired by https://stackoverflow.com/a/11233293
def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))

    logger = logging.getLogger(name)
    logger.setLevel(level)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False

    return logger
