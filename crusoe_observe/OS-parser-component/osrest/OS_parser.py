from json import load
import pkg_resources
from .method import UserAgent, Domain, Tcpml
import structlog


def merge_results(ips, useragent, domain, tcpml):
    """Merge results of the methods
    :param ips: list of investigated IPs
    :param useragent: result of UserAgent method
    :param domain: result of Domain method
    :param tcpml: result of Tcpml method
    :return: Merged results
    """
    result = {}
    for ip in ips:
        result[ip] = {}

    for ip, os_dict in tcpml.items():
        tmp = result[ip]
        for os_name, prob in os_dict.items():
            tmp[os_name] = tmp.get(os_name, 0) + prob

    for ip, os_dict in useragent.items():
        tmp = result[ip]
        for os_name, prob in os_dict.items():
            tmp[os_name] = tmp.get(os_name, 0) + prob

    for ip, os_dict in domain.items():
        tmp = result[ip]
        for os_name, prob in os_dict.items():
            updated = False
            for present_name in tmp:
                if os_name in present_name:
                    tmp[present_name] += prob
                    updated = True
            if not updated:
                tmp[os_name] = prob

    return result


def finalize_results(results):
    """Inspect results and select the most probable OS
    :param results: dictionary of results with probabilities
    :return: dictionary of IPs with the most probable OS assigned
    """
    out = {}
    for ip, result in results.items():
        final = "Unknown"
        best = 0
        apple = 0
        darwin = 0
        iOS = 0
        Mac = 0

        for OS in result:
            if "Darwin" in OS:
                apple += result[OS]
                darwin += result[OS]
            elif "iOS" in OS:
                iOS += result[OS]
                darwin += result[OS]
            elif "Mac OS X" in OS:
                apple += result[OS]
                Mac += result[OS]
            if result[OS] > best:
                final = OS
                best = result[OS]

        if "Darwin" in final or "iOS" in final or "Mac" in final:
            out[ip] = final
            continue

        if apple > (best * 3):
            if Mac >= darwin and Mac >= iOS:
                out[ip] = "Mac OS X"
                continue
            if iOS >= darwin:
                out[ip] = "iOS"
                continue
            out[ip] = "Darwin"
            continue

        out[ip] = final

    return out


def cpe_form(raw_result, cpe_list, logger):
    """ Convert result into CPE format by specified cpe_list
    """
    result = {}
    names = cpe_list.keys()
    for ip, os in raw_result.items():
        os_cpe = "*:*:*"
        for name in names:
            if name in os:
                os_version = os[len(name) + 1:]
                if os_version not in cpe_list[name]["versions"]:
                    if os_version != '':
                        logger.warning(f"Unknown version for OS: {os}")
                    os_version = "*"
                os_cpe = f"{cpe_list[name]['product']}:{os_version}"
                break

        result[ip] = os_cpe
    return result


def make_sessions(flows, config={}, logger=structlog.get_logger(), cpe=True):
    """Parse flows and aggregate it to sessions by src ip
    :param flows: flows to analysis
    :return: list of joined IP address with OS as sessions
    """
    def filename(name):
        """
        Obtain filename for the resource
        """
        return pkg_resources.resource_filename(__name__, name)

    tcpml_model_path = config["tcpml_model"] if "tcpml_model" in config.keys() else "/var/tmp/crusoe/os_model.pkl"
    tcpml_dataset_path = config["tcpml_dataset"] if "tcpml_dataset" in config.keys() else "/usr/share/crusoe/os_dataset.csv"

    try:
        model = Tcpml.load_model(tcpml_model_path)
    except FileNotFoundError:
        try:
            dataset = Tcpml.load_dataset(tcpml_dataset_path)
        except FileNotFoundError:
            logger.error("Training dataset could not be found!")
            return {}
        model = Tcpml.build_model(dataset)
        Tcpml.save_model(model, tcpml_model_path)

    methods = {
        "useragent": UserAgent(),
        "domain": Domain(filename("data/config.ini")),
        "tcpml": Tcpml(filename("data/num2os.json"), model)
    }

    ips = list(map(lambda x: x["sa"], filter(lambda x: "sa" in x, flows)))

    if len(ips) == 0:
        logger.warning("Zero flows obtained!")
        return {}

    useragent = methods["useragent"].run(flows)
    domain = methods["domain"].run(flows)
    tcpml = methods["tcpml"].run(flows)

    result_raw_data = merge_results(ips, useragent, domain, tcpml)

    result = finalize_results(result_raw_data)

    if cpe:
        cpe_path = filename("data/os.json")
        with open(cpe_path, 'r') as cpef:
            cpe_list = load(cpef)
        result = cpe_form(result, cpe_list, logger)

    return result

