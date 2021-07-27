"""Service Identifier module

This module identifies network services based on Machine Learning with ground
truth estabilished via NBAR2 apptag from real traffic.
"""
import datetime
import ipaddress
import json
import os
import time
import traceback

import joblib
import numpy as np
import pandas
import sklearn.tree

# Mapping of protocols to integral values, 0 default
PROTOCOL_MAP = {
    "TCP": 1,
    "UDP": 2,
}

"""
Transform protocol name to integral value
:param x: protocol name
:return: protocol integral value
"""
def trans_proto(x):
    return PROTOCOL_MAP.get(x, 0)

"""
Transform string to float and interpret SI quantifiers
:param x: string
:return: float
"""
def trans_float(x):
    try:
        return float(x)
    except ValueError:
        if x == "" or x.find('N/A') != -1:
            raise ValueError
        elif x.find('K') != -1:
            return round(float(x.split(' ')[0]) * 2 ** 10, 2)
        elif x.find('M') != -1:
            return round(float(x.split(' ')[0]) * 2 ** 20, 2)
        elif x.find('G') != -1:
            return round(float(x.split(' ')[0]) * 2 ** 30, 2)
        elif x.find('T') != -1:
            return round(float(x.split(' ')[0]) * 2 ** 40, 2)

"""
Transform string to float and interpret SI quantifiers; return 0.0 if transformation fails
:param x: string
:return: float
"""
def trans_float_nothrow(x):
    try:
        return trans_float(x)
    except ValueError:
        return 0.0

"""
Transform string to int and interpret SI quantifiers
:param x: string
:return: int
"""
def trans_int(x):
    try:
        return int(x)
    except ValueError:
        return int(trans_float(x))

"""
Transform string to int and interpret SI quantifiers; return 0 if transformation fails
:param x: string
:return: int
"""
def trans_int_nothrow(x):
    try:
        return int(x)
    except ValueError:
        return int(trans_float_nothrow(x))


# flow field name, transformation function
FEATURES = [("pr", trans_proto)
           ,("pkt", trans_int)
           ,("bpp", trans_int)
           ,("tos", lambda x: trans_int(x) >> 2)
           ,("tcpsynsize", trans_int_nothrow)]

FEATURE_NAMES = list(map(lambda x: x[0], FEATURES))

INFO = ["ts", "sa", "sp", "da", "dp", "apptag"]

class ServiceIdentifier:
    """ServiceIdentifier class

    This class provides interface to machine learning pipeline for
    identification of services from network flow data.

    Input flow should be in JSON format and should contain following fields:
      pr - protocol name
      pkt - number of flow packets
      bpp - bytes per packet
      tos - type of service
      ndavg - average inter-packet delay
      ndmin - minimal inter-packet delay
      ndmax - maximal inter-packet delay
      tcpsynsize - size of the first (SYN) TCP packet
    """

    """Initialize ServiceIdentifier
    :param paths: dictionary with keys model, dataset, nbar which contain paths
    to corresponding files.
    :param target_network: list of networks whose services to recognize
    :param logger: instance of logger
    """
    def __init__(self, paths, target_network, logger):
        self.logger = logger
        self.logger.info("Initialize")

        self.target_network = target_network

        self.logger.info(f"Loading model from \"{paths['model']}\"")
        if not os.path.exists(paths["model"]):
            self.logger.info("Trained model not found.")
            self.logger.info(f"Loading training dataset from \"{paths['dataset']}\"")

            if not os.path.exists(paths["dataset"]):
                self.logger.error("Training dataset not found!")
                raise FileNotFoundError("Training dataset not found!")

            self.model = self.build_model(paths["dataset"])
            self.save_artifact(self.model, paths["model"])
        else:
            self.model = self.load_artifact(paths["model"])

        if os.path.exists(paths["nbar"]):
            with open(paths["nbar"]) as source:
                self.nbar = json.load(source)
        else:
            self.logger.error("Cisco NBAR2 reference not found!")
            raise FileNotFoundError("Cisco NBAR2 reference not found!")

    """Load training dataset to memory
    :param path: path to the training dataset
    :return: dataset as pandas dataframe
    """
    def load_training(self, path):
        return pandas.read_csv(
            path,
            delimiter=";",
            dtype=dict(zip(list(FEATURE_NAMES) + ["apptag"], [np.float32] * len(FEATURE_NAMES) + [str]))
        )

    """Load input flows
    :param flows: path to the flows or loaded json
    :return: (preprocessed flow features, additional flow information)
    """
    def load_flows(self, flows):
        invalid = 0
        features = []
        info = []
        if isinstance(flows, str):
            with open(flows) as source:
                data = json.load(source)
        else:
            data = flows

        for row in data:
            flow_features = []
            flow_info = []
            for key in FEATURES:
                value = row.get(key[0])
                if value == None:
                    invalid += 1
                    break
                try:
                    flow_features.append(key[1](value))
                except ValueError:
                    invalid += 1
                    break
            else:
                features.append(flow_features)
                for key in INFO:
                    flow_info.append(row.get(key, ""))

                info.append(flow_info)

        self.logger.info(f"{invalid} invalid records in flow data.")

        return np.array(features), info

    """Builds model from given data
    :param path: path to training dataset
    :return: trained model
    """
    def build_model(self, path):
        self.logger.info("Building model")

        training_data = self.load_training(path)

        training_targets = training_data["apptag"]
        training_data = training_data.drop("apptag", axis=1)

        model = sklearn.tree.DecisionTreeClassifier()
        model.fit(training_data, training_targets)
        return model


    """Saves any object (artifact) to specified location.
    :param artifact: object to be saved
    :param path: path where the object should be saved
    """
    def save_artifact(self, artifact, path):
        self.logger.info(f"Saving artifact to \"{path}\"")

        joblib.dump(artifact, path)

    """Loads an artifact from given location.
    :param path: path to the saved object
    :return: the loaded object
    """
    def load_artifact(self, path):
        self.logger.info(f"Loading artifact from \"{path}\"")

        return joblib.load(path)

    """Runs the component
    :param path: path to JSON of flow data to perform the prediction on
    :return: results formatted for upload to DB
    """
    def run(self, data):
        self.logger.info("Predicting")
        features, info = self.load_flows(data)

        services = self.model.predict(features)

        # substitute apptags with names from NBAR reference
        services = list(map(lambda x: self.nbar[x] if x in self.nbar.keys() else x, services))

        servers, clients = self.aggregate(features, info, services)

        return self.format_output(servers, clients)

    """Get server info from flow info
    :param features: flow features
    :param info: additional flow information
    :return: (IP, port, protocol) of the presumed server; None if not recognized
    """
    def get_server(self, features, info):
        pr = features[FEATURE_NAMES.index("pr")]
        sa = info[INFO.index("sa")]
        da = info[INFO.index("da")]
        sp = int(info[INFO.index("sp")])
        dp = int(info[INFO.index("dp")])

        if pr == PROTOCOL_MAP["TCP"]:
            return (da, dp, "TCP") if features[FEATURE_NAMES.index("tcpsynsize")] != 0 else None

        if pr == PROTOCOL_MAP["UDP"]:
            if dp > 49152 and sp <= 49152:
                return (sa, sp, "UDP")
            if sp > 49152 and dp <= 49152:
                return (da, dp, "UDP")

        return None

    """Get client ip from flow info and server ip
    :param server_ip: server ip
    :param info: additional flow information
    :return: IP of the presumed client; None if not recognized
    """
    def get_client(self, server_ip, info):
        if info[INFO.index("sa")] == server_ip:
            return info[INFO.index("da")]
        elif info[INFO.index("da")] == server_ip:
            return info[INFO.index("sa")]

        return None

    """Aggregate detected services by servers
    :param features: list of flow features
    :param info: list of flow additional infomation
    :param services: list of detected services
    :return: (server_result, client_result) where server_result is tuple of
        (ip, port, protocol, service, timestamp); and client_result is a tuple of
        (server_ip, client_ip, service, timestamp).
    """
    def aggregate(self, features, info, services):
        servers = {}
        clients = {}
        for flow_feature, flow_info, flow_service in zip(features, info, services):
            if flow_service == "0:0": # skip unknown services
                continue

            server = self.get_server(flow_feature, flow_info) # get server tuple

            if server == None: # server not recognized
                continue

            server_ip = ipaddress.ip_address(server[0])
            if not any(map(lambda x: server_ip in ipaddress.ip_network(x), self.target_network)):
                continue

            ts = datetime.datetime.strptime(flow_info[0], "%Y-%m-%d %H:%M:%S.%f").astimezone().isoformat()

            # Add client to client list
            client = self.get_client(server[0], flow_info)
            client_ip = ipaddress.ip_address(client)
            if any(map(lambda x: client_ip in ipaddress.ip_network(x), self.target_network)):
                if server not in clients.keys():
                    clients[server] = {}
                if client not in clients[server]:
                    clients[server][client] = []
                clients[server][client].append(ts)

            # Add service detection timestamp
            if server not in servers.keys():
                servers[server] = {}

            if flow_service not in servers[server].keys():
                servers[server][flow_service] = []

            servers[server][flow_service].append(ts)

        # Server Aggregate
        server_aggregate = {}
        for server in servers.keys():
            s = max(servers[server].items(), key=lambda x: len(x[1]))
            ts = max(s[1])

            server_aggregate[server] = (s[0], ts)

        # Get latest timestamp in clients
        client_result = []
        clients_keys = list(clients.keys())
        for key in clients_keys:
            for client_ip, tss in clients[key].items():
                client_result.append((key[0], client_ip, server_aggregate[key][0], max(tss)))

        # Flatten servers
        server_result = []
        for server in server_aggregate.items():
            server_result.append((*server[0], *server[1]))

        return server_result, client_result

    """Format output for database import
    :param service_result: list of tuples of detected services
    :param client_result: list of tuples of detected clients
    :return: database associations
    """
    def format_output(self, service_result, client_result):
        service_output = [
            {
                "ip": item[0],
                "port": item[1],
                "protocol": item[2],
                "service": item[3],
                "timestamp": item[4]
            } for item in service_result
        ]
        client_output = [
            {
                "server": item[0],
                "client": item[1],
                "service": item[2],
                "timestamp": item[3]
            } for item in client_result
        ]

        return service_output, client_output
