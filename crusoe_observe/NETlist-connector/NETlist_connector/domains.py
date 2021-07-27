#!/usr/bin/python3

import json
from pkg_resources import resource_filename
from netaddr import IPAddress
from netaddr.core import AddrFormatError
from dns import resolver, exception
from shutil import copyfile
import concurrent.futures
import structlog

DOMAIN_SUFIX = '_domain.json'
PATH = resource_filename(__name__, 'data/subnets')
RESOLVED = 0
IGNORED = 0
NOTRESOLVED = 0
DATA = {}
RESOLVE = resolver.Resolver()
RESOLVE.timeout = 2
RESOLVE.lifetime = 2
logger = structlog.get_logger()


def get_domain_name_from_ip(ip):
    """
    Resolve domain name for given IP
    :param ip: string, Input IP
    :return: None
    """
    global RESOLVED
    global IGNORED
    global NOTRESOLVED
    try:
        reverse = IPAddress(ip).reverse_dns
        answer = RESOLVE.query(reverse, "PTR")
        RESOLVED += 1
        domains = []
        for rdata in answer:
            domains.append(str(rdata))
        DATA.update(dict({ip: domains}))
    except AddrFormatError:
        logger.error(f"Invalid format of ip address: {str(ip)} \n")
        IGNORED += 1
    except resolver.NXDOMAIN:
        logger.warning(f"NXDOMAIN error for ip address: {str(ip)} \n")
        datapom = dict({ip: "Domain name not found"})
        DATA.update(datapom)
        NOTRESOLVED += 1
    except resolver.NoNameservers:
        logger.warning(f"Nameservers failed to answer the query: {str(ip)}\n")
        datapom = dict({ip: "Domain name not found"})
        DATA.update(datapom)
        NOTRESOLVED += 1
    # Catch other exception raised by dns.resolver
    except exception.DNSException as ex:
        logger.warning(f"Exception \"{ex}\" from dns module happened on: {str(ip)}\n")
        datapom = dict({ip: "Domain name not found"})
        DATA.update(datapom)
        NOTRESOLVED += 1


def gen_new_dns_json():
    """
    Generate json file with IPs and their respective domains.
    :return: Stats about domains
    """
    json_dict = []
    for ip in DATA.keys():
        entry = {'ip': ip, 'domain': DATA.get(ip)}
        json_dict.append(entry)
    dist = {"domains": json_dict}
    with open(f'{PATH}{DOMAIN_SUFIX}', 'w') as out_file:
        out_file.write(json.dumps(dist, indent=2, sort_keys=True))
    stat = len(dist["domains"])
    return f'{stat} IPs were processed. '


def update_domain_names(iplist, neo4j_import, log):
    """
    Try to resolve domain names and update them to db, using newly created json
    :param iplist: List of all :IP nodes in database
    :param neo4j_import: neo4j import path
    :param log: logger instance
    :return: None
    """
    global logger
    logger = log

    with concurrent.futures.ThreadPoolExecutor(max_workers=64) as pool:
        pool.map(get_domain_name_from_ip, iplist)

    stat_final = gen_new_dns_json()
    if NOTRESOLVED != 0:
        stat_final += f'{NOTRESOLVED} out of them were not RESOLVED. '
    if IGNORED != 0:
        stat_final += f'{IGNORED} out of them has been IGNORED due to invalid format. '
    if RESOLVED != 0:
        stat_final += f'{RESOLVED} successfully RESOLVED. '

    copyfile(f'{PATH}{DOMAIN_SUFIX}', f'{neo4j_import}{DOMAIN_SUFIX}')

    return stat_final
