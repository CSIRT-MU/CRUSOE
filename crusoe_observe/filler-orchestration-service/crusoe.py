import celery_logger
import json
import os
import random
import services_component
import sys
import uuid
from NETlist_connector.subnetParser import NETlist
from celery import Task, Celery, group
from celery.signals import task_prerun, worker_ready
from cmsscan.scanner import scanner as cmsscanner
from configparser import SafeConfigParser, ConfigParser
from cve_connector.nvd_cve.toneo4j import move_cve_data_to_neo4j
from cve_connector.vendor_cve.implementation.main import add_vendor_cves
from criticality_estimator import CriticalityEstimator
from datetime import datetime, timedelta, timezone
from flowmon_m import flowmon_connector
from ipaddress import IPv4Address, IPv4Network
from neo4j.exceptions import TransientError
from neo4jclient.AbsClient import AbstractClient
from neo4jclient.CMSClient import CMSClient
from neo4jclient.NmapClient import NmapClient
from neo4jclient.OSClient import OSClient
from neo4jclient.RTIRClient import RTIRClient
from neo4jclient.RESTClient import RESTClient
from neo4jclient.ServicesClient import ServicesClient
from neo4jclient.VulnerabilityCompClient import VulnerabilityCompClient
from neo4jclient.WebCheckerClient import WebCheckerClient
from neo4jclient.Cleaner import Cleaner
from nmap_topology_scanner.scanner import scan, topology_scan_neo
from osrest import run
from rtir_connector import rtir
from sabu import JsonParsing
from shadowserver_module import Shadowserver
from shodan_module import Shodan
from shutil import copyfile
from time import time, sleep
from webchecker_component import Webchecker

# Create the app
# GLOBAL CONSTANTS & METHODS #

DEBUG = False
APP = Celery('CRUSOE')
APP.config_from_object('celeryconfig')
CONFIG_PATH = 'config/conf.ini'
logger = celery_logger.get_logger("CELERY", "/var/log/crusoe/celery.log")


def parse_config(section_name):
    """
    Parse config file
    :param section_name: name of config section
    :return: section of config with same name as dictionary
    """
    config = ConfigParser()
    config.read(CONFIG_PATH)
    return config[section_name]


def edit_config(section, key, value):
    """
    Edit actual config
    :param section: name of config section
    :param key: key of section
    :param value: value to edit
    """
    parser = SafeConfigParser()
    parser.read(CONFIG_PATH)
    parser.set(section, key, value)
    with open(CONFIG_PATH, 'w') as conf_file:
        parser.write(conf_file)


def realize_transaction(neo4jclient_function, args=None):
    """
    Realize transaction between neo4j and this program methods.
    :param neo4jclient_function: function to be executed
    :param args: function argument
    :return: result of function
    """
    for i in range(9, -1, -1):
        try:
            if args is None:
                return neo4jclient_function()
            else:
                return neo4jclient_function(args)
        except TransientError:
            logger.warning(f"Other transaction ongoing, waiting {0.5 * (10 - i)} second and trying again")
            logger.warning(f"Attempts left: {i}")
            sleep(0.5 * (10 - i))


# CONFIG #


class ComponentException(Exception):
    """
    Exception from component
    """
    pass


class BaseTask(Task):
    """
    Task base class
    """
    crusoe_conf = parse_config('crusoe')
    flowmon_conf = parse_config('flowmon')
    os_conf = parse_config('os')
    service_conf = parse_config('service')
    sabu_conf = parse_config('sabu')
    nmap_topology_scanner_conf = parse_config('nmap-topology-scanner')
    rtir_conf = parse_config('rtir-connector')
    cve_connector_conf = parse_config('cve-connector')
    shadowserver_conf = parse_config('shadowserver')
    shodan_conf = parse_config('shodan')
    webchecker_conf = parse_config('webchecker')
    cms_conf = parse_config('cms')
    # the most used params
    neo4j_addr = parse_config('neo4j')['address']
    neo4j_passwd = parse_config('neo4j')['password']
    neo4j_import = parse_config('neo4j')['import']
    log_path = crusoe_conf['log_path']
    tmp_path = crusoe_conf['tmp']

    def now(self):
        """Return the current time and date as a datetime."""
        return datetime.now(self.timezone)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """
        Retry handler
        """
        logger.warning(f"retried task {task_id}")

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """
        Handler called after the task returns
        """
        if status == "SUCCESS":
            logger.debug(f"{task_id} ended with status :{status} and return {retval}")
        else:
            logger.warning(f"{task_id} ended with status :{status} and return {retval}")

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        Error handler
        """
        logger.error(f'{task_id} failed: {exc} with {einfo}')


@worker_ready.connect
def setup_DB(sender, **kwargs):
    """
    Initial setup
    """
    if "crusoe" in sender.hostname:
        logger.info("Master is running initial setup")
        # Clean up all waiting task
        APP.control.purge()
        # Setup initial structure of DB
        neo4j_pass = parse_config('neo4j')['password']
        neo4j_addr = parse_config('neo4j')['address']
        AbstractClient(bolt=neo4j_addr, password=neo4j_pass).init_db()
        # send waiting task to remote scan
        # APP.send_task("remote.scan_init", queue='remote')
    else:
        logger.info("Only master can create initial setup")


@task_prerun.connect
def per_task_setup(sender, task_id, task, args, kwargs, **_kwargs):
    """
    Before task start handler
    """
    logger.info(f"started task {task.name}")


# TASKS #


@APP.task(bind=True, base=BaseTask)
def rtir_connector(self):
    """
    RTIR connector task
    """
    rtir_result = rtir.parse_rt(user=self.rtir_conf['user'],
                                password=self.rtir_conf['password'],
                                output=f"{self.neo4j_import}{self.rtir_conf['file']}",
                                logger=celery_logger.get_logger("RTIR", f"{self.log_path}rtir_connector.log"))
    neo4jclient = RTIRClient(bolt=self.neo4j_addr, password=self.neo4j_passwd)
    realize_transaction(neo4jclient.create_rtir_part, f"{self.rtir_conf['file']}")
    return rtir_result

@APP.task(bind=True, base=BaseTask)
def scan_init(self):
    indexes = list(range(42)) + list(range(55, 58)) + list(range(59, 106)) + list(range(107, 256))
    subnets = [f"147.251.{x}.0/24" for x in indexes]
    for subnet in subnets:
        APP.send_task("remote.topology_scan", queue='crusoe', kwargs = {"subnet" : subnet})
        APP.send_task("remote.vertical_scan", queue='crusoe', kwargs = {"subnet" : subnet})


@APP.task(bind=True, base=BaseTask, soft_time_limit=86400)
def topology_scan(self, subnet):
    # enqueue the same task
    APP.send_task("remote.topology_scan", queue='crusoe', kwargs = {"subnet" : subnet})
    result, raw_result = topology_scan_neo([subnet])
    client = NmapClient(bolt=self.neo4j_addr, password=self.neo4j_passwd)
    client.create_topology(json.dumps(result))
    return len(result)


@APP.task(bind=True, base=BaseTask, soft_time_limit=86400)
def vertical_scan(self, subnet):
    # enqueue the same task
    APP.send_task("remote.vertical_scan", queue='crusoe', kwargs = {"subnet" : subnet})
    result = scan([subnet], '-sV -T4 -F')
    client = NmapClient(bolt=self.neo4j_addr, password=self.neo4j_passwd)
    client.create_vertical_scan_cpe(json.dumps(result))
    return len(result)

@APP.task(bind=True, base=BaseTask, soft_time_limit=86400)
def shadowserver(self):
    """
    Shadowserver task
    """
    stats = Shadowserver.process_vulnerabilities(self.tmp_path, self.shadowserver_conf['user'],
                                                 self.shadowserver_conf['password'], self.neo4j_import,
                                                 self.shadowserver_conf['json_name'],
                                                 celery_logger.get_logger("Shadowserver",
                                                                          f"{self.log_path}vulnerability_component_shadowserver.log"))
    vuln_client = VulnerabilityCompClient(bolt=self.neo4j_addr, password=self.neo4j_passwd)
    realize_transaction(vuln_client.create_shadowserver_part, f"{self.shadowserver_conf['json_name']}")
    return stats


@APP.task(bind=True, base=BaseTask)
def shodan(self):
    """
    Shodan task
    """
    stats = Shodan.process_vulnerabilities(self.shodan_conf['config_file'],
                                           self.shodan_conf['api_key'],
                                           self.shodan_conf['subnets'],
                                           self.neo4j_import,
                                           self.shodan_conf['json_name'],
                                           celery_logger.get_logger("Shodan",
                                                                    f"{self.log_path}vulnerability_component_shodan.log"))
    vuln_client = VulnerabilityCompClient(bolt=self.neo4j_addr, password=self.neo4j_passwd)
    realize_transaction(vuln_client.create_shadowserver_part,
                        f"{self.shodan_conf['json_name']}")
    return stats


@APP.task(bind=True, base=BaseTask)
def cleaner(self):
    """
    Neo4j cleaner task
    """
    cleaner_client = Cleaner(bolt=self.neo4j_addr, password=self.neo4j_passwd)

    number_of_deleted_sec_events = cleaner_client.clean_security_event()
    number_of_deleted_resolves_to = cleaner_client.clean_old_domains()
    number_of_deleted_connected_to = cleaner_client.clean_topology()
    number_of_deleted_net_services = cleaner_client.clean_network_services()
    number_of_deleted_soft_versions = cleaner_client.clean_software_versions()

    return f'Successfully deleted {number_of_deleted_sec_events} security event nodes, ' \
           f'{number_of_deleted_resolves_to} :RELATES_TO relationships, ' \
           f'{number_of_deleted_connected_to} :IS_CONNECTED_TO relationships, ' \
           f'{number_of_deleted_net_services + number_of_deleted_soft_versions} :ON relationships'


@APP.task(bind=True, base=BaseTask)
def sabu(self):
    """
    Sabu task
    """
    return JsonParsing.parse(self.sabu_conf['directory'],
                             self.neo4j_passwd,
                             self.sabu_conf['regex'],
                             self.sabu_conf['path'],
                             self.neo4j_import,
                             celery_logger.get_logger("SABU", f"{self.log_path}sabu.log"))

@APP.task(bind=True, base=BaseTask)
def netlist(self):
    """
    Netlist task
    """
    nl = NETlist(self.neo4j_passwd, f"/var/lib/neo4j/import/subnets",
                 celery_logger.get_logger("NETlist", f"{self.log_path}netlist.log"))
    return nl.update()


@APP.task(bind=True, base=BaseTask, soft_time_limit=14400, max_retries=5)
def nvd_CVEs(self):
    """
    Adds or updates all CVEs which were modified the current day
    :return:
    """
    cve_data = f"{self.tmp_path}{self.cve_connector_conf['tmp_cve_subdir']}"
    specified_time = (datetime.now() - timedelta(days=1)).isoformat()
    try:
        return move_cve_data_to_neo4j(specified_time, self.neo4j_passwd, cve_data,
                                      celery_logger.get_logger("CVE", f"{self.log_path}cve.log"))
    except:
        logger.error(f"Unexpected error: {sys.exc_info()[0]}")
        raise self.retry(countdown=4 ** self.request.retries)


@APP.task(bind=True, base=BaseTask, soft_time_limit=14400, max_retries=5)
def vendor_CVEs(self):
    """
    Adds or updates all vendor CVEs
    """
    ms_directory = f"{self.tmp_path}{self.cve_connector_conf['tmp_ms_subdir']}"
    try:
        return add_vendor_cves(ms_directory, self.neo4j_passwd, celery_logger.get_logger("CVE", f"{self.log_path}cve.log"))
    except:
        logger.error(f"Unexpected error: {sys.exc_info()[0]}")
        raise self.retry(countdown=4 ** self.request.retries)


# FLOWS #

@APP.task(bind=True, base=BaseTask)
def OS_parse(self, args):
    """
    Parse OS for endpoint devices by outcoming flows
    """
    t1 = time()
    result = run.parse(args[1],
                       f"{self.neo4j_import}{self.os_conf['file']}",
                       config=self.os_conf,
                       logger=celery_logger.get_logger("OS", f"{self.log_path}os_detection.log"))
    t2 = time()
    logger.info('Commit to database ...')
    neo4jclient = OSClient(bolt=self.neo4j_addr, password=self.neo4j_passwd)
    realize_transaction(neo4jclient.upload_os_from_file, f"{self.os_conf['file']}")
    t3 = time()

    return f'{result} Measurement: python = {t2 - t1} neo = {t3 - t2}'


@APP.task(bind=True, base=BaseTask, soft_time_limit=600)
def service(self, args):
    """
    Parse services by outcoming flows
    """
    t1 = time()
    result = services_component.run(args[1],
                                    f"{self.neo4j_import}{self.service_conf['output']}",
                                    config=self.service_conf,
                                    logger=celery_logger.get_logger("SERVICES", f"{self.log_path}services_component.log"))
    logger.info("Commiting services to database ...")
    t2 = time()
    neo4jclient = ServicesClient(bolt=self.neo4j_addr, password=self.neo4j_passwd)
    realize_transaction(neo4jclient.create_service_component, f"{self.service_conf['output']}")
    t3 = time()

    return f'{result} Measurement: python = {t2 - t1} neo = {t3 - t2}'


@APP.task(bind=True, base=BaseTask, ignore_result=True)
def check_certs(self):
    """
    Webchecker task
    """
    t1 = time()
    wc = Webchecker(self.webchecker_conf, celery_logger.get_logger("WEBCHECKER", f"{self.log_path}webchecker.log"))
    t2 = time()
    db = WebCheckerClient(bolt=self.neo4j_addr, password=self.neo4j_passwd)
    hosts = list(map(lambda x: (x[0]["IP"], x[0]["Domain"]), db.get_ip_and_domain_names()))
    t3 = time()
    result = wc.run_certs(hosts)

    with open(f"{self.neo4j_import}{self.webchecker_conf['cert_file']}", "w") as cert_file:
        json.dump(result, cert_file)
    t4 = time()

    db.upload_cert_errors(f"{self.webchecker_conf['cert_file']}")
    t5 = time()

    return f"{len(result['data'])} certificate issues found. Measurement: python = {(t2 - t1) + (t4 - t3)} neo = {(t3 - t2) + (t5 - t4)}"


@APP.task(bind=True, base=BaseTask, ignore_result=True)
def detect_domains(self, args):
    """ parse domains by incoming flows"""
    t1 = time()
    wc = Webchecker(self.webchecker_conf, celery_logger.get_logger("WEBCHECKER", "/var/log/crusoe/webchecker.log"))
    result = wc.run_detect(args[1])

    with open(f"{self.neo4j_import}{self.webchecker_conf['domain_file']}", "w") as cert_file:
        json.dump(result, cert_file)
    t2 = time()

    db = WebCheckerClient(bolt=self.neo4j_addr, password=self.neo4j_passwd)
    db.upload_hostnames(f"{self.webchecker_conf['domain_file']}")
    t3 = time()

    return f"{len(result['data'])} domains detected. Measurement: python = {t2 - t1} neo = {t3 - t2}"


@APP.task(bind=True, base=BaseTask, ignore_result=True)
def compute_criticality(self):
    """
    Criticality estimator task
    """
    ce = CriticalityEstimator(
        bolt=self.neo4j_addr,
        password=self.neo4j_passwd,
        logger=celery_logger.get_logger("CRITICALITY", f"{self.log_path}criticality.log")
    )
    return ce.run()


@APP.task(bind=True, max_retries=6, ignore_result=True, base=BaseTask)
def flowmon(self, param_prefix):
    """
    Download flows
    """
    try:
        path, counter = flowmon_connector.download_ssh(
            user=self.flowmon_conf['user'],
            password=self.crusoe_conf['passphrase'],
            key_path=self.crusoe_conf['key_path'],
            hostname=self.flowmon_conf['hostname'],
            nfdump_path=self.flowmon_conf['nfdump_path'],
            dir_param=self.flowmon_conf['dir_param'],
            collectors=json.loads(self.flowmon_conf['collectors']),
            aggregate=self.flowmon_conf[f'{param_prefix}aggregate'],
            flow_filter=self.flowmon_conf[f'{param_prefix}filter'],
            output_format=self.flowmon_conf[f'{param_prefix}format'],
            remote_file_path=self.flowmon_conf[f'{param_prefix}remote_file_path'],
            local_tmp_path=f"{self.flowmon_conf['tmp_dir']}{self.flowmon_conf[param_prefix + 'local_file_prefix']}",
            logger=celery_logger.get_logger("flowmon", f"{self.log_path}flowmon.log"))
        if counter == 0:
            logger.error(f"Missing flow data")
            if self.request.retries == self.max_retries:
                raise ComponentException("Flowmon: missing flow data")
            raise self.retry(countdown=2 ** self.request.retries)
    except:
        logger.error(f"Unexpected error: {sys.exc_info()[0]}")
        if self.request.retries == self.max_retries:
            raise ComponentException(f"Flowmon: unexpected error: {sys.exc_info()[0]}")
        raise self.retry(countdown=2 ** self.request.retries)
    return f'Processed scan flag: {param_prefix[:-1]}, number of flows: {counter}', path


@APP.task(bind=True, base=BaseTask, ignore_result=True)
def flowmon_chain(self):
    """
    Download flows, parse os, services and domains
    """
    sleep(5)
    out_group = group(OS_parse.s(), service.s())
    out_flow_chain = (flowmon.s(param_prefix="out_") | out_group)
    in_flow_chain = (flowmon.s(param_prefix="in_") | detect_domains.s())
    out_flow_chain()
    in_flow_chain()
    logger.info(f'remove {self.flowmon_conf["tmp_dir"]} directory')

    now = time()
    for f in os.listdir(os.path.join(self.flowmon_conf["tmp_dir"])):
        file_path = os.path.join(self.flowmon_conf["tmp_dir"], f)
        if "~" in file_path or os.stat(file_path).st_mtime < now - 3600:
            os.remove(file_path)

    start_time = datetime.now() - timedelta(minutes=5)
    end_time = start_time + timedelta(minutes=5)
    start_time = start_time.astimezone().isoformat()
    end_time = end_time.astimezone().isoformat()
    return f'Processing flows between: {start_time} and {end_time}, active components: domains, OS and services'


@APP.task(bind=True, base=BaseTask, ignore_result=True)
def cms_scan(self):
    """
    CMS component task
    """
    blacklist = list(range(42, 55)) + [58, 106]
    blacklist = [IPv4Network(f"147.251.{x}.0/24") for x in blacklist]
    client = CMSClient(bolt=self.neo4j_addr, password=self.neo4j_passwd)
    res = client.get_ips_and_domain_names().value()
    stats = 0
    with open(self.cms_conf["tmp"], "w") as out:
        for host in res:
            if any([IPv4Address(host["IP"]) in x for x in blacklist]):
                continue
            out.write(f"{host['Domain']}\n")
            stats += 1

    result = cmsscanner.run(whatweb_path=self.cms_conf["whatweb_path"],
                            hosts=self.cms_conf["tmp"],
                            extra_params=self.cms_conf["params"],
                            out_path=f"{self.neo4j_import}{self.cms_conf['json_name']}",
                            logger=celery_logger.get_logger("CMS", f"{self.log_path}cms.log"))
    if result:
        client.create_cms_component(f"{self.cms_conf['json_name']}")
        return f"Scanned {stats} domains"
    return f"Empty result JSON, nothing to parse. Exiting..."
