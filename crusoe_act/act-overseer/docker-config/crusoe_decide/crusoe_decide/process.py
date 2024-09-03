"""
Module process.py contains functionality of the decision support analytical process.
"""

import os
from configparser import ConfigParser
from datetime import datetime
import pkg_resources
import structlog
from neo4jclient.AttackGraphClient import AttackGraphClient
from neo4jclient.MissionAndComponentClient import MissionAndComponentClient
import crusoe_decide.bayes as bayes
import crusoe_decide.generator as generator
import crusoe_decide.run_mulval as run_mulval
from crusoe_decide.components import get_mission_components

attack_graphs = {}
CONFIG_PATH = pkg_resources.resource_filename(__name__, "data/conf.ini")


def analytical_process(
        neo4j_pas,
        neo4j_bolt="bolt://localhost:7687",
        logger=structlog.get_logger()
):
    """
    Main function of the whole analytical process.

    :param neo4j_pas: password to Neo4j database
    :param neo4j_bolt: bolt on which the Neo4j database runs
    :param logger: logger for logging progress of algorithm and time information
    :return: For each mission its most resilient configuration.
    """
    client = AttackGraphClient(bolt=neo4j_bolt, password=neo4j_pas, encrypted=True)
    mission_client = MissionAndComponentClient(bolt=neo4j_bolt, password=neo4j_pas, encrypted=True)
    logger.info("Procedure analytical_process() started")
    attack_graphs.clear()

    # parse config and get paths
    config = ConfigParser()
    config.read(CONFIG_PATH)
    attack_graph = config['attack-graph']
    mulval_dir = attack_graph['mulval_dir']

    vertices_file = os.path.join(mulval_dir, 'VERTICES.CSV')
    arcs_file = os.path.join(mulval_dir, 'ARCS.CSV')
    input_file = os.path.join(mulval_dir, 'input_file.P')

    missions = client.get_all_mission_names()
    combinations = get_possible_configurations(mission_client, missions, logger=logger)

    # analytical process itself with added data operations
    config_dict = {}
    time_dict = {}
    for mission in combinations:
        index = 0
        logger.info(f"Processing mission {mission}")
        mission_start = datetime.now()
        config_dict[mission] = {}
        for configuration in combinations[mission]:
            logger.info(f"Hosts count: {len(configuration)}")
            logger.info(f"Configuration: {str(configuration)}")
            data = mission_client.load_json_from_property(mission).single()['json_structure']
            config_dict[mission][index] = \
                process_configuration(mission, vertices_file, arcs_file, configuration, data,
                                      input_file, mulval_dir, client, logger=logger)
            index += 1
        mission_end = datetime.now()
        time_diff = (mission_end - mission_start).total_seconds()
        logger.info(
            f"Processed mission, mission {mission} takes "
            f"{time_diff} seconds")
        time_dict[mission] = time_diff

    result_dict = get_results(combinations, config_dict)
    create_output_data(combinations, config_dict, client)

    logger.info(f"Generated attack graphs: {attack_graphs}")
    return result_dict


def get_results(combinations, config_dict):
    """
    This function finds for each mission its most resilient configuration and probability.

    :param combinations: dictionary which contains for each mission its configurations
    :param config_dict: dictionary which contains for each configuration and goal host
    the inferred probabilities (C, I, A)
    :return: dictionary which contains for each mission only its most resilient configuration
    and probability
    """
    result_dict = {}
    for mission in combinations:
        result_dict[mission] = {}
        for index in config_dict[mission]:
            partial_result = {}
            for host in config_dict[mission][index]:
                if "probability" not in partial_result or \
                        sum(config_dict[mission][index][host]['result']) > \
                                sum(partial_result["probability"]):
                    partial_result["configuration"] = combinations[mission][index]
                    partial_result["probability"] = config_dict[mission][index][host]['result']
            if "probability" not in result_dict[mission] or \
                    sum(partial_result["probability"]) < sum(result_dict[mission]["probability"]):
                result_dict[mission]['configuration'] = partial_result["configuration"]
                result_dict[mission]["probability"] = partial_result["probability"]
    return result_dict


def create_output_data(combinations, config_dict, ag_client):
    """
    Creates representation of results in the Neo4j database. Results are stored as properties
    of :Configuration nodes and as properties of edges of type :CONTAINS between configuration
    and its hosts.

    :param combinations: dictionary containing for each mission its configurations
    :param config_dict: dictionary containing results for each mission, configuration and host
    :param ag_client: neo4j client
    :return: timestamp of creation
    """
    timestamp = datetime.now().isoformat()
    for mission in combinations:
        for index in config_dict[mission]:
            # processing one configuration
            neo4j_hosts = ag_client.get_hosts_for_configuration(mission, index+1)
            configuration_maximum = (0, 0, 0)
            if neo4j_hosts:
                # configuration already exists in the DB
                for host_id in combinations[mission][index]:
                    host_result = config_dict[mission][index][host_id]['result']
                    hostname = config_dict[mission][index][host_id]['hostname']
                    ag_client.set_host_configuration_properties(
                        hostname, mission, index + 1, host_result[0], host_result[1],
                        host_result[2]
                    )
                    if sum(configuration_maximum) < sum(host_result):
                        configuration_maximum = host_result
            else:
                # configuration does not exist
                ag_client.create_configuration(mission, timestamp, index+1)
                for host_id in combinations[mission][index]:
                    host_result = config_dict[mission][index][host_id]['result']
                    hostname = config_dict[mission][index][host_id]['hostname']
                    ag_client.add_host_to_configuration(hostname, mission, index+1, host_result[0],
                                                        host_result[1], host_result[2])
                    if sum(configuration_maximum) < sum(host_result):
                        configuration_maximum = host_result
            ag_client.set_configuration_properties(mission, index + 1,
                                                   configuration_maximum[0],
                                                   configuration_maximum[1],
                                                   configuration_maximum[2], timestamp)
    return timestamp


def get_possible_configurations(client, missions, logger=structlog.get_logger()):
    """
    Returns configurations for each mission in the list of missions.

    :param client: neo4j client
    :param missions: list of missions
    :param logger: logger for logging progress of algorithm and time information
    :return: configurations for missions
    """
    result_dict = {}
    logger.info("Determining all configurations.")

    for mission in missions:
        data = client.load_json_from_property(
            mission['mission']['name']).single()['json_structure']
        for item in data['nodes']['missions']:
            if item['name'] == mission['mission']['name']:
                mission_id = item['id']
                break
        result_dict[mission['mission']['name']] = get_mission_components(data, mission_id)
    return result_dict


def process_configuration(mission, vertices_file, arcs_file, configuration, data, input_file,
                          mulval_dir, client, logger):
    """
    This function processes one configuration.

    :param mission: name of mission
    :param vertices_file: path to the file with vertices generated by MULVAL
    :param arcs_file: path to the file with arcs generated by MULVAL
    :param configuration: set of hosts = configuration
    :param data: json containing constrained AND-OR tree
    :param input_file: path to the input file for MULVAL
    :param mulval_dir: path to the output MULVAL directory
    :param client: neo4j client
    :param logger: logger for logging progress of algorithm and time information
    :return: a tuple containing probabilities for confidentiality, integrity and availability,
    i.e. (C, I, A) for the specific configuration
    """
    partial_results = {}
    hosts = []
    for host_id in configuration:
        for host in data['nodes']['hosts']:
            if host['id'] == host_id:
                hosts.append(host)

    max_conf = 0
    max_integ = 0
    max_avail = 0
    for host in hosts:
        # logger.info(f"Goal has id: {host['id']}")
        # delete both files and when the check whether attack graph was generated is needed
        # we check only existence of files
        if os.path.exists(vertices_file):
            os.remove(vertices_file)
        if os.path.exists(arcs_file):
            os.remove(arcs_file)

        generator.generate_input_file(mission, host, hosts, input_file, mulval_dir, client,
                                      logger=logger)
        run_mulval.run_mulval(CONFIG_PATH, logger=logger)

        if os.path.exists(vertices_file):
            if mission in attack_graphs:
                attack_graphs[mission] += 1
            else:
                attack_graphs[mission] = 1

        cia_tuple = bayes.convert_attack_graph_to_bayesian(arcs_file, vertices_file, client,
                                                           logger=logger)
        (actual_conf, actual_integ, actual_avail) = cia_tuple

        if actual_conf > max_conf:
            max_conf = actual_conf
        if actual_integ > max_integ:
            max_integ = actual_integ
        if actual_avail > max_avail:
            max_avail = actual_avail
        partial_results[host['id']] = {}
        partial_results[host['id']]['hostname'] = host['hostname']
        partial_results[host['id']]['result'] = (round(actual_conf, 4), round(actual_integ, 4),
                                                 round(actual_avail, 4))
    return partial_results
