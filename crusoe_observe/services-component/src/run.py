import json
import datetime
import pkg_resources
from .services import Antivirus
from .services import ServiceIdentifier
import structlog
import ipaddress


def round_time(time):
    """
    Get time of last flowmon export.
    :param time: current time.
    :return: rounded time.
    """
    t_min = time.minute % 5
    t_sec = time.second
    t_mic = time.microsecond
    time = time - datetime.timedelta(minutes=t_min, seconds=t_sec, microseconds=t_mic)
    return time


def run(flow_path, session_path, config={}, logger=structlog.get_logger()):
    """Run method executes this component on given data and writes the result
    to given output file.
    :param flow_path: path to file containing input flow data
    :param session_path: path to file where the output shall be put
    :param config: component config dict
    :param logger: logger instance
    :return: result message
    """
    target_network = json.loads(config["target_network"]) if "target_network" in config.keys() else ["0.0.0.0/0"]
    target_network = list(map(ipaddress.ip_network, target_network))

    si_paths = {
        "model": config["si_model"] if "si_model" in config.keys() else "/var/tmp/crusoe/si_model.pkl",
        "dataset": config["si_dataset"] if "si_dataset" in config.keys() else "/usr/share/crusoe/si_dataset.csv",
        "nbar": pkg_resources.resource_filename(__name__, "data/si_nbar.json"),
    }

    now = round_time(datetime.datetime.now()).astimezone().isoformat()

    logger.info("Start")

    try:
        with open(flow_path, 'r') as flow_file:
            flows = json.load(flow_file)
            logger.info("Flows loaded", count=len(flows))
    except IOError:
        logger.error("Could not read flow file", path=flow_path)
        return "Could not read flow file"

    av = Antivirus(pkg_resources.resource_filename(__name__, "data/av.json"), target_network, logger.bind(module="antivirus"))

    try:
        si = ServiceIdentifier(si_paths, target_network, logger.bind(module="service_identifier"))
    except:
        si = None
        logger.error("Initialization of Service Identifier subcomponent was not successful!")

    antivirus = []
    try:
        antivirus += av.run(flows)
    except KeyError:
        logger.error("Antivirus detection failed. A flow does not contain required fields.")

    si_services = []
    si_clients = []
    if si is not None:
        si_result = si.run(flows)
        si_services += si_result[0]
        si_clients += si_result[1]

    new_session = {
        "time": now,
        "antivirus": antivirus,
        "services": si_services,
        "clients": si_clients,
    }

    try:
        with open(session_path, 'w') as session_file:
            json.dump(new_session, session_file)
    except IOError:
        logger.error("Could not write flow file", path=session_path)
        return "Could not write flow file"

    antivirus_total_count = len(antivirus)
    services_total_count = len(si_services)
    clients_total_count = len(si_clients)

    logger.info("Finish (antivirus)", count=antivirus_total_count)
    logger.info("Finish (services)", count=services_total_count)
    logger.info("Finish (clients)", count=clients_total_count)

    return f"Antivirus: {antivirus_total_count}, services: {services_total_count}, clients: {clients_total_count}."
