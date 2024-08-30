from json import JSONEncoder


class Encoder(JSONEncoder):
    """
    Custom JSON encoder for encoding recommender output.
    """

    def default(self, o):
        """
        Encodes given object in its JSON representation. If given class
        contains method to_json, then it is used for encoding. Default encoding
        is used otherwise (in case of primitive data types etc.)
        :param o: Object to be encoded in JSON
        :return: JSON representation
        """
        if "to_json" in dir(o):
            return o.to_json()
        return JSONEncoder.default(self, o)
