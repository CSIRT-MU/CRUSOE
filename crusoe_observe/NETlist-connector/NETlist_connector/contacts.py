#!/usr/bin/python3

import json
from pkg_resources import resource_filename
from netaddr import IPNetwork, IPAddress
from netaddr.core import AddrFormatError
import structlog

IP_SUFIX = '_ip.json'
CONTACTS_SUFIX = '_contacts.json'
PATH = resource_filename(__name__, 'data/subnets')
logger = structlog.get_logger()


def best_fit(data):
    """
    Detect best fit Subnet for ip
    :param data: array of possible subnets
    :return: Best fit subnet
    """
    best = None
    size = 0
    for subnet in data:
        if best is None:
            best = subnet
            size = data[subnet]
        else:
            if data[subnet] == size:
                logger.warning(f'{subnet} and {best} are same!')
            if data[subnet] < size:
                best = subnet
                size = data[subnet]
    return best


def create_json(result):
    """
    Create json-like structure out of data
    :param result: data from which will structure be created
    :return: Json structured data
    """
    json_dict = []
    for ip, data in result.items():
        result = {'ip': ip, 'bestFit': best_fit(data), 'subnets': list(data.keys())}
        json_dict.append(result)
    return json_dict


def gen_new_ip_json(csv_data, hosts, log):
    """
    Generate json with data about IPs and theirs Subnets
    :param csv_data: entry data
    :param hosts: Array of IPs
    :param log: instance logger
    :return: Stats about newly created json
    """
    global logger
    logger = log

    result = {}
    for subnet in csv_data:
        parse_subnet(subnet.get('range'), result, hosts)
    json_dict = create_json(result)
    dist = {"collection": json_dict}
    stat = len(dist["collection"])
    with open(f'{PATH}{IP_SUFIX}', 'w') as out_file:
        out_file.write(json.dumps(dist, indent=2, sort_keys=True))
    if stat == 0:
        return 'No new IPs -> No new assigned subnets.'
    return f'Subnet was assigned to {stat} IPs. '


def parse_subnet(subnet_name, result, hosts):
    """
    For all :hosts check if they are in given :subnet_name.
    Result is stored in :result
    :param subnet_name: range of subnet
    :param result: store result in this structure
    :param hosts: IPs without :PART_OF relationship in neo4j
    :return: None
    """
    # IPAddress('147.251.0.0')
    try:
        subnet = IPNetwork(subnet_name)
    except AddrFormatError:
        logger.error(f"Invalid subnet {subnet_name}")
        return

    # number of unique addresses
    subnet_size = subnet.size

    for ip in hosts:
        # check for invalid ip formats from rtir-connector
        try:
            if IPAddress(ip) in subnet:
                ip_str = str(ip)
                if ip_str not in result:
                    result[ip_str] = {}
                result[ip_str][subnet_name] = subnet_size
        except (AddrFormatError, ValueError) as e:
            logger.error(f"Invalid format of IP {ip}")
            logger.error(f"{e}")


def gen_new_contact_json(csv_data):
    """
    Generate json with data about Subnets and theirs Contacts
    :param csv_data: entry data
    :return: Stats about created subnets
    """
    dist = {"subnets": csv_data}
    with open(f'{PATH}{CONTACTS_SUFIX}', 'w') as out_file:
        out_file.write(json.dumps(dist, indent=2, sort_keys=True))
    stat = len(dist["subnets"])
    return f'Reloaded {stat} subnets and their contacts. '
