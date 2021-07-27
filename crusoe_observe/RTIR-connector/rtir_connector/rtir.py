#!/usr/local/bin/python3.7

"""
Module for parsing information from RTIR
"""

from datetime import date, timedelta, datetime
import json
import re
from pytz import timezone
import requests
import structlog
import pkg_resources


# https://rt.csirt.muni.cz/REST/1.0/search/ticket?query=?Queue='Automatic'%20AND%20Created=%20'2018-08-12''
# https://rt.csirt.muni.cz/REST/1.0/ticket/457096

TIMEZONE = timezone('Europe/Prague')
CREATOR_REGEX = re.compile(r'(?<=^Creator: ).*', re.MULTILINE)
SUBJECT_REGEX = re.compile(r'(?<=^Subject: ).*', re.MULTILINE)
REQUESTOR1_REGEX = re.compile(r'(?<=^Requestors: ).*', re.MULTILINE)
REQUESTOR2_REGEX = re.compile(r'(?<=^\W{12}).*', re.MULTILINE)
CREATED_REGEX = re.compile(r'(?<=^Created: ).*', re.MULTILINE)
CATEGORY_REGEX = re.compile(r'(?<=^CF\.{Category}: ).*', re.MULTILINE)
IP_REGEX = re.compile(r'(?<=^CF\.{ActorIP}: ).*', re.MULTILINE)


def filename(name):
    """
    Obtain filepath for the resource
    """
    return pkg_resources.resource_filename(__name__, name)


def download_data(session, url, login, logger=structlog.get_logger()):
    """
    Download data from RT server
    :param session: requests persistent session
    :param url: url of server
    :param login: credentials
    :param logger: module logger
    :return: Tickets if any, in text form
    """
    try:
        result = session.post(url, data=login)
        if "Your username or password is incorrect" in result.text:
            raise requests.HTTPError("Invalid credentials")
    except requests.RequestException as exception:
        logger.error("Can't connect or sign into RT system", error_message=exception)
        raise requests.RequestException("Can't connect or sign into RT system")
    logger.info("Data downloaded")
    return result.text


def requestors(data, logger=structlog.get_logger()):
    """
    Parse requestors from given data
    :param data: data which will be examined
    :param logger: module logger
    :return: requestors if any, empty array otherwise
    """
    result = []
    matches = REQUESTOR1_REGEX.search(data)
    matches2 = REQUESTOR2_REGEX.search(data)
    if not matches:
        logger.info("Requestors not found")
        return []
    result.append(matches.group(0).split(','))
    if matches2:
        result.append(matches2.group(0).split(','))
    result = result[0]
    for i, entry in enumerate(result):
        result[i] = entry.strip()
    logger.info("Requestors added")
    return result


def parse_ticket(session, uri, login, ticket_id, logger=structlog.get_logger()):
    """
    Parse relevant information from ticket
    :param session: request persistent session
    :param uri:  url of server
    :param login: credentials
    :param logger: module logger
    :param ticket_id: ID of ticket which will be parsed
    :return: result with information
    """
    data = download_data(session, f'{uri}/ticket/{ticket_id}', login)
    result = {'id': ticket_id, 'creator': CREATOR_REGEX.search(data).group()}
    raw_subject = SUBJECT_REGEX.search(data).group()
    if '/' in raw_subject:
        raw_subject = raw_subject.split('/ ')[1]
    result['subject'] = raw_subject
    result['requestor'] = requestors(data)
    my_date = CREATED_REGEX.search(data).group()
    my_date = datetime.strptime(my_date, '%a %b %d %H:%M:%S %Y').astimezone(TIMEZONE).isoformat()
    result['created'] = my_date
    result['category'] = CATEGORY_REGEX.search(data).group()
    result['ip'] = IP_REGEX.search(data).group()
    logger.info(f'Ticket with ID {ticket_id} was parsed')
    return result


def parse_rt(user, password, output='/var/lib/neo4j/import/rtir.json', uri='https://rt.csirt.muni.cz/REST/1.0',
             subnet_filter="CF.{ActorIP} >= '147.251.' AND CF.{ActorIP} < '147.252.'",
             last_day=True, logger=structlog.get_logger()):
    """
    Parse new tickets from RT system
    :param user: username for RT system
    :param password: password for RT system
    :param output: where the final JSON will be stored
    :param uri: url of RT server
    :param subnet_filter: Filter for subnets (only parse tickets from our subnet)
    :param last_day: filter for date (usually only last day is examined)
    :param logger: module logger
    :return: Number of added tickets
    """
    logger.info(f'RTIR connector started')
    login = {'user': user, 'pass': password}
    session = requests.Session()
    session.verify = filename('certs/cert_file.crt')

    q_filter = f"/search/ticket?query=?Queue='Automatic' AND {subnet_filter}"
    if last_day:
        my_date = (date.today() - timedelta(1)).strftime('%Y-%m-%d')
        q_filter = f"{q_filter} AND Created>='{my_date}'"
        logger.info("parsing last day")
    ticket_list = download_data(session, f'{uri}{q_filter}', login).split('\n')

    ticket_array = []
    for line in ticket_list:
        if ':' in line:
            ticket_array.append(line.split(':')[0])
    logger.info(f'{len(ticket_array)} tickets found')
    result = {'rtir': []}
    for ticket in ticket_array:
        result['rtir'].append(parse_ticket(session, uri, login, ticket))
    with open(output, 'w') as out_file:
        logger.info(f'preparing JSON output')
        json.dump(result, out_file)
    logger.info(f'Done')
    return f'Added tickets in last 2 days: {len(ticket_array)}'
