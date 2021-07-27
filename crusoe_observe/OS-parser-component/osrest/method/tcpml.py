"""OS identification method using netflows -- TCP/IP Machine Learning

This module contains implementation of Tcpml class which is a method for OS
identification via TCP/IP parameters using machine learning (Decision Tree
Classifier). The method requires two setup files -- training dataset in format
`OS Num;TCP window size;TCP syn size;TCP TTL`, and JSON file with mapping
between OS Num and corresponding OS name.
"""

from math import ceil, log
import json
import os.path

from sklearn.tree import DecisionTreeClassifier
import joblib
import numpy
import pandas as pd
import structlog


class Tcpml:
    """Tcpml OS identification technique

    This class provides an interface for performing OS identification based on
    netflow data.
    """
    TCP_PARAMS = ["tcpwinsize", "tcpsynsize", "tcpttl"]
    WIN_MAP = {'Windows 10.0': 'Windows 10',
               'Windows 6.3': 'Windows 8.1',
               'Windows 6.2': 'Windows 8',
               'Windows 6.1': 'Windows 7',
               'Windows 6.0': 'Windows Vista',
               'Windows 5.2': 'Windows XP Professional x64',
               'Windows 5.1': 'Windows XP',
               'Windows 5.0': 'Windows 2000'}

    API_MAP = {#'Android 1': 'Android 1.0',
               #'Android 2': 'Android 1.1',
               #'Android 3': 'Android 1.5',
               #'Android 4': 'Android 1.6',
               #'Android 5': 'Android 2.0',
               #'Android 6': 'Android 2.0',
               #'Android 7': 'Android 2.1',
               #'Android 8': 'Android 2.2.x',
               #'Android 9': 'Android 2.3',
               'Android 10': 'Android 2.3',
               'Android 11': 'Android 3.0',
               'Android 12': 'Android 3.1',
               'Android 13': 'Android 3.2',
               'Android 14': 'Android 4.0',
               'Android 15': 'Android 4.0',
               'Android 16': 'Android 4.1',
               'Android 17': 'Android 4.2',
               'Android 18': 'Android 4.3',
               'Android 19': 'Android 4.4',
               'Android 21': 'Android 5.0',
               'Android 22': 'Android 5.1',
               'Android 23': 'Android 6.0',
               'Android 24': 'Android 7.0',
               'Android 25': 'Android 7.1',
               'Android 26': 'Android 8.0',
               'Android 27': 'Android 8.1',
               'Android 28': 'Android 9'}

    @staticmethod
    def load_dataset(path):
        """Loads dataset from a file
        :param path: path to the dataset
        :return: pair of features and labels
        """
        data_frame = pd.read_csv(path, delimiter=";")
        features = data_frame.loc[:, "TCP window size":]
        labels = data_frame["OS Num"]
        return (features, labels)

    @staticmethod
    def build_model(dataset):
        """Builds a model and returns it
        :param path: path to the dataset; if unset, default path is used
        "return: trained model
        """
        model = DecisionTreeClassifier()
        model.fit(*dataset)
        return model

    @staticmethod
    def save_model(model, path):
        """Save model to given path
        :param model: model to save
        :param path: path to the file where the model shall be stored (.pkl)
        """
        joblib.dump(model, path)

    @staticmethod
    def load_model(path):
        """Loads model from a file
        :return: the model
        """
        return joblib.load(path)

    @classmethod
    def flow_has_tcp(cls, flow):
        """Check whether a flow contains TCP parameters
        :param flow: flow represented as a dictionary
        :return: true if the flow contains TCP parameters; false otherwise
        """
        return all(map(lambda x: x in flow.keys(), cls.TCP_PARAMS)) \
            and all(map(lambda x: x != "N/A", map(lambda x: flow[x], cls.TCP_PARAMS)))

    @classmethod
    def convert_win(cls, os_name):
        """
        Convert windows version to windows name
        :param os: windows version
        :return: windows name
        """
        return cls.WIN_MAP.get(os_name, os_name)

    @classmethod
    def convert_api(cls, os_name):
        """
        Convert Android API version to OS version
        :param os: Android string with API version
        :return: Android sring with OS version
        """
        return cls.API_MAP.get(os_name, os_name)

    def __init__(self, mapping_path, model, logger=structlog.get_logger()):
        """Constructs a new instance of Tcpml class
        :param mapping_path: path to JSON file containing mapping between OS
        num and OS name
        :param model: either path to model or training dataset, or the model
        itself
        """
        if isinstance(model, str):  # path
            if os.path.splitext(model)[1] == ".pkl":  # to prebuilt model
                self.model = self.load_model(model)
            else:  # to training dataset
                self.model = self.build_model(self.load_dataset(model))
        else:  # it is already built model
            self.model = model

        with open(mapping_path, "r") as num2os_file:
            self.num2os = json.load(num2os_file)

        self.logger = logger.bind(method="tcpml")

    def predict(self, data):
        """Use a model to perform prediction on given data
        :param model: trained model
        :param data: array-like object of data samples for prediction
        :return: list (of dictionaries between OS and its predicted
        probability) for each sample
        """
        predictions = self.model.predict_proba(data)
        result = []
        for probs in predictions:
            sample = {}
            for num, prob in enumerate(probs):
                if prob != 0.0:
                    sample[self.convert_api(self.convert_win(self.num2os[str(num)]))] = prob
            result.append(sample)
        return result

    def run(self, flows):
        """Run the method on given flows
        :param flows: flows to process
        :return: dictionary between IPs and predicted operating systems
        """
        self.logger.info("Method start")

        def predicate(flow):
            return "sa" in flow and self.flow_has_tcp(flow)

        flows = list(filter(predicate, flows))

        sas = numpy.empty(len(flows), dtype=object)
        features = numpy.zeros((len(flows), 3))

        for idx, flow in enumerate(flows):
            try:
                sas[idx] = flow["sa"]
                features[idx][0] = flow["tcpwinsize"]
                features[idx][1] = flow["tcpsynsize"]
                # TTL roundup
                features[idx][2] = int(pow(2, ceil(log(int(flow["tcpttl"]), 2))))
            except KeyError as e:
                self.logger.warning('Flow is missing a necessary key!', key=str(e))
            except Exception as e:
                self.logger.warning(f'Exception while processing flow!', exception=str(e), flow=str(flow))

        predictions = self.predict(features)

        result = {}

        # aggregate by ip
        for sa, prediction in zip(sas, predictions):
            result[sa] = result.get(sa, {})
            for os_name, prob in prediction.items():
                result[sa][os_name] = result[sa].get(os_name, 0) + prob

        # normalize probabilities
        for sa in result:
            total = sum(result[sa].values())
            for os_name in result[sa].keys():
                result[sa][os_name] /= total

        self.logger.info("Method finish")

        return result
