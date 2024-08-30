from json import dumps
from utils.json_encoder import Encoder


class JsonOutput:
    """
    Exports recommender script output in JSON file.
    """
    @staticmethod
    def json_export(host_list, file_path):
        """
        Exports recommended host list in a JSON file.
        :param host_list: List of recommended hosts
        :param file_path: Path to JSON file
        :return: None
        """
        with open(file_path, "w") as writer:
            writer.write(dumps(host_list, indent=4, cls=Encoder))
