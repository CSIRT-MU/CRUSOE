#!/usr/bin/python3

from requests.packages.urllib3.exceptions import InsecureRequestWarning
from pkg_resources import resource_filename
from hashlib import md5
from netaddr import IPNetwork
from netaddr.core import AddrFormatError
from dns import resolver
from shutil import copyfile
from neo4j.exceptions import TransientError
from time import time, sleep
from NETlist_connector.contacts import gen_new_ip_json, gen_new_contact_json
from NETlist_connector.domains import update_domain_names
from neo4jclient.NETlistClient import NETlistClient
import structlog
import requests
import csv

IP_SUFIX = '_ip.json'
CONTACTS_SUFIX = '_contacts.json'
DATA_SUFIX = '_data.txt'
DOMAIN_SUFIX = '_domain.json'
PATH = resource_filename(__name__, 'data/subnets')


class NETlist:
    """
    Main class of the component.
    """
    def __init__(self, neo4j_pass, neo4j_import, logger=structlog.get_logger()):
        self.neo4jclient = NETlistClient(password=neo4j_pass)
        self.neo4j_import = neo4j_import
        self.resolve = resolver.Resolver()
        self.logger = logger

    def realize_transaction(self, neo4jclient_function, args=None):
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
                return neo4jclient_function(args)
            except TransientError:
                self.logger.warning("Other transaction ongoing, waiting 0.5 second and trying again")
                self.logger.warning(f"Attempts left: {i}")
                sleep(0.5)

    def check_and_update(self, hosts):
        """
        Check if exist newer version of subnets.
        If not, update only nodes without subnets
        Otherwise, reload network layer in database according to new subnet file.
        :param hosts: array of IPs without subnet in DB
        """
        with open(f'{PATH}{DATA_SUFIX}', 'a') as check:
            check.write('')
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        new_file = requests.get("https://webserver.ics.muni.cz/internal/IPadresy/site.txt").text
        new_hash = md5(new_file.encode('utf-8')).hexdigest()
        old_hash = md5(open(f'{PATH}{DATA_SUFIX}', 'rb').read()).hexdigest()
        subnets_array = self.create_subnet_array(new_file)
        if new_hash != old_hash:
            self.realize_transaction(self.neo4jclient.delete_NETlist_component)
            results = self.realize_transaction(self.neo4jclient.get_ips_without_subnet).value()

            self.logger.info("Load new contact file")

            stat1 = gen_new_ip_json(subnets_array, results, self.logger)
            stat2 = gen_new_contact_json(subnets_array)

            copyfile(f'{PATH}{IP_SUFIX}', f'{self.neo4j_import}{IP_SUFIX}')
            copyfile(f'{PATH}{CONTACTS_SUFIX}', f'{self.neo4j_import}{CONTACTS_SUFIX}')

            self.realize_transaction(self.neo4jclient.create_NETlist_component, f'subnets{CONTACTS_SUFIX}')
            self.realize_transaction(self.neo4jclient.update_NETlist_component, f'subnets{IP_SUFIX}')
            self.logger.info(f"stat1: {stat1}")
            self.logger.info(f"stat2: {stat2}")

            return stat1 + stat2
        elif hosts:
            stat1 = gen_new_ip_json(subnets_array, hosts, self.logger)

            copyfile(f'{PATH}{IP_SUFIX}', f'{self.neo4j_import}{IP_SUFIX}')

            self.realize_transaction(self.neo4jclient.update_NETlist_component, f'subnets{IP_SUFIX}')
            self.logger.info(f"stat1: {stat1}")
            return stat1
        return ""

    def create_subnet_array(self, subnet_file):
        """
        Parse data from subnet_file and save them into suitable structure
        :param subnet_file:
        :return: Parsed data
        """
        with open(f'{PATH}{DATA_SUFIX}', 'w') as contacts:
            contacts.write(subnet_file)

        csv_dict_reader = csv.reader(subnet_file.splitlines(), delimiter=';')
        subnets_array = []
        for row in csv_dict_reader:
            try:
                IPNetwork(row[0].strip())
                csv_data = dict(range=row[0].strip(), organization=row[1].strip(), note=row[2].strip(),
                                contacts=[x.strip() for x in row[3].split(',')])
                subnets_array.append(csv_data)
            except AddrFormatError:
                self.logger.error(f"INVALID SUBNET {row[0].strip()}")
        return subnets_array

    def update(self):
        """
        Initialize db connection, create constraints and update db  .
        :return: Stats about component
        """
        results = self.realize_transaction(self.neo4jclient.get_ips_without_subnet).value()
        ips_without_domain = self.realize_transaction(self.neo4jclient.get_our_subnet_without_domain_name).value()
        start = time()
        stat2 = self.check_and_update(results)
        end = time()
        self.logger.info(f"It took {end-start:.2f} seconds to add subnet to {len(results)} ips.")
        start2 = time()
        stat1 = update_domain_names(iplist=ips_without_domain, neo4j_import=self.neo4j_import, log=self.logger)
        self.realize_transaction(self.neo4jclient.create_NETlist_resolves_to, f'subnets{DOMAIN_SUFIX}')
        end2 = time()
        self.logger.info(f"It took {end2-start2:.2f} seconds to resolve {len(ips_without_domain)} ips.")
        return stat1 + stat2
