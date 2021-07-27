#!/usr/bin/python3.6

"""
Module is used for acquiring information about Content management systems
"""

import json
import subprocess
import structlog
import pkg_resources


def parse(data_path, out_path, cpe_path, logger):
    """
    Parse output of scanning and map CMS names and versions to the CPE format
    :param data_path: path to the file with data acquired from scanning
    :param out_path: path to the file, where the output will be saved
    :param cpe_path: path to the file with information about services which this component detects,
                     by default a data/cms.json can be used.
    :param logger: logger instance
    :return: Results
    """
    with open(cpe_path, 'r') as cpefile:
        cpe_dict = json.load(cpefile)

    with open(data_path, 'r') as datafile:
        try:
            data = json.load(datafile)
        except json.JSONDecodeError as e:
            logger.info(f'Empty result JSON, nothing to parse. Exiting...')
            return False

    raw_results = {}
    with open(out_path, 'w') as outfile:
        for host in data:
            print(host)
            if "plugins" not in host or "IP" not in host["plugins"]:
                continue
            ip = host["plugins"]["IP"]['string'][0]
            ip_cpes = set()

            for key in host["plugins"]:
                if key in cpe_dict:
                    if 'version' in host["plugins"][key]:
                        if "-" in host["plugins"][key]['version'][0]:
                            version = host["plugins"][key]['version'][0][:host["plugins"][key]['version'][0].find("-")]
                        else:
                            version = host["plugins"][key]['version'][0]
                        if version in cpe_dict[key]['versions']:
                            ip_cpes.add(cpe_dict[key]['product'] + ":" + version)
                        else:
                            ip_cpes.add(cpe_dict[key]['product'] + ":*")
                    else:
                        ip_cpes.add(cpe_dict[key]['product'] + ":*")
            if ip not in raw_results:
                raw_results[ip] = set()
            for cpe in ip_cpes:
                raw_results[ip].add(cpe)
        results = []
        for key, values in raw_results.items():
            host_data = {"ip": key, "cpe": (list(values))}
            results.append(host_data)
        json.dump({"data": results}, outfile)
    return results


def run(whatweb_path, hosts, extra_params, out_path, cpe_path="", logger=structlog.get_logger(), is_file=True):
    """
    Scan webs for CMS, save results
    :param whatweb_path: Path to the WhatWeb tool.
    :param hosts: list of webs which will be scanned/or path to the file in case of is_file=True
    :param extra_params: optional parameters of whatweb utility
    :param out_path: path to the file, where results will be stored
    :param cpe_path: path to the file with information about services which this component detects,
                     by default a data/cms.json is used.
    :param logger: logger instance, by default structlog printlogger
    :param is_file: True if hosts are read from file, False otherwise
    :return: None
    """
    if cpe_path == "":
        cpe_path = pkg_resources.resource_filename(__name__, "../data/cms.json")
    if is_file:
        hosts = f"-i {hosts}"
    tmp_path = "/tmp/scan.json"
    with open(tmp_path, 'w') as log:
        pass
    command = f"{whatweb_path} {extra_params} {hosts} --log-json={tmp_path}"
    logger.info(command)
    subprocess.run([command], shell=True)
    res = parse(tmp_path, out_path, cpe_path, logger)
    if res:
        logger.info(f"{len(res)} IPs were detected")
    return res
