#!/usr/bin/python3
from time import sleep
from json import JSONDecodeError, dump, load
from datetime import datetime, timedelta, timezone
from .OS_parser import make_sessions
import os
import structlog


def round_time(my_time):
    """
    Get time of last flowmon export.
    :param time: current time.
    :return: rounded time.
    """
    t_min = my_time.minute % 5
    t_sec = my_time.second
    t_mic = my_time.microsecond
    my_time = my_time - timedelta(minutes=t_min, seconds=t_sec, microseconds=t_mic)
    return my_time


def get_prev_sessions(sessions_path, logger=structlog.get_logger()):
    """
    Parse json file to sessions
    :param sessions_path: path to json file
    :return: dictionary of sessions in format dict[ip] = os
    """
    with open(sessions_path, 'r') as prev_sessions:
        result = {}
        try:
            sessions = load(prev_sessions)
            if 'new' in sessions:
                for record in sessions['new']:
                    result[record['ip']] = record['os']
            if 'inactive' in sessions:
                for record in sessions['inactive']:
                    result[record['ip']] = record['os']
            if 'changed' in sessions:
                for record in sessions['changed']:
                    result[record['ip']] = record['os']
            if 'unchanged' in sessions:
                for record in sessions['unchanged']:
                    result[record['ip']] = record['os']
            return result

        except (ValueError, JSONDecodeError) as e:
            logger.error(str(e))
            return {}


def write_session(prev_sessions, sessions, start_time, end_time, session_path, logger=structlog.get_logger()):
    """
    Rewrite json file with new data
    :param prev_sessions: old sessions
    :param sessions: new sessions
    :param time: timestamp of processed flows
    :param session_path: path to json file
    :return: None
    """
    with open(session_path, 'w') as session_file:
        # create json structure
        data = {}
        data['start_time'] = start_time.astimezone().isoformat()
        data['end_time'] = end_time.astimezone().isoformat()
        data['new'] = []
        data['unchanged'] = []
        data['changed'] = []
        data['inactive'] = []

        for key, val in sessions.items():
            if key not in prev_sessions:
                data['new'].append({"ip": key, "os": val})
                continue
            if val == prev_sessions[key]:
                data['unchanged'].append({"ip": key, "os": val})
            else:
                data['changed'].append({"ip": key, "os": val})
        for key, val in prev_sessions.items():
            if key not in sessions:
                data['inactive'].append({"ip": key, "os": val})

        try:
            dump(data, session_file)
        except IOError:
            logger.error("Could not write os sessions", path=session_path)
            raise
    return f"New: {len(data['new'])}, unchanged: {len(data['unchanged'])}, changed: {len(data['changed'])}, inactive: {len(data['inactive'])} sessions"


def parse(flow_path, session_path, config={}, logger=structlog.get_logger(), cpe=True):
    """
    Main part of used components
    is steps:
    - load configuration
    - load password if is necessary and is missing in config file
    - create tmp file for neo4j
    loop:
    - download last flowmon data
    - analysis of data
    - load previous sessions
    - rewrite new sessions
    :return: None
    """
    logger.info('OS detection is starting')
    if not os.path.exists(session_path):
        logger.info('create session file for OS history')
        with open(session_path, 'a') as session:
            session.write('{}')

    end_time = round_time(datetime.now())
    start_time = end_time - timedelta(minutes=5)

    if not os.path.exists(flow_path):
        raise FileNotFoundError(f"Flow data are missing, processing time: {datetime.now()}, proccessing data: {flow_path}")

    with open(flow_path, 'r') as flow_file:
        flow = load(flow_file)

    logger.info(f'parsed flows: {len(flow)}')
    if len(flow) == 10000:
        logger.warning("You are at limit with rest output, try filter only HTTP/HTTPS or smaller IP address range")

    sessions = make_sessions(flow, config, logger, cpe)
    logger.info(f'sessions: {len(sessions)}')
    prev_sessions = get_prev_sessions(session_path, logger)
    answer = write_session(prev_sessions, sessions, start_time, end_time, session_path, logger)
    logger.info(f'{end_time} done')
    return answer
