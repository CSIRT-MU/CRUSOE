#!/usr/bin/env python3
"""
Module contains functionality which exports appropriate system variables
and runs MULVAL on the input file.
"""

from shutil import copyfile
import os
from configparser import ConfigParser
import pkg_resources


def run_mulval(config_path, logger):
    """
    This function runs MULVAL attack graph generation.

    :param config_path: path to the config file
    :param logger: logger for logging progress of algorithm and time information
    :return: None
    """
    config = ConfigParser()
    config.read(config_path)
    attack_graph = config['attack-graph']

    mulvalroot = attack_graph['mulval_root']
    xsbroot = attack_graph['xsb_root']
    mulval_dir = attack_graph['mulval_dir']
    rules_file = attack_graph['interaction_rules_file']

    os.environ['MULVALROOT'] = mulvalroot
    os.environ['XSBROOT'] = xsbroot
    path = os.environ['PATH']
    os.environ['PATH'] = f'{path}:{mulvalroot}/bin:{mulvalroot}/utils:{xsbroot}/bin:{xsbroot}/build'

    source_rules = pkg_resources.resource_filename(__name__, "data/crusoe_rules.P")
    if not os.path.exists(f'{mulvalroot}/kb/{rules_file}'):
        copyfile(source_rules, f'{mulvalroot}/kb/{rules_file}')

    decide_dir = os.getcwd()
    os.chdir(mulval_dir)
    # -v means in pdf, -l option means output is only in .csv format
    # following command generates attack graph in pdf
    # os.system(f'graph_gen.sh input_file.P -v -p -r {mulvalroot}/kb/{rules_file}')
    os.system(f'graph_gen.sh input_file.P -l -p -r {mulvalroot}/kb/{rules_file}')
    logger.info("MULVAL attack graph generation completed.")
    os.chdir(decide_dir)
