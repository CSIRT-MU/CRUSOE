from json import dumps, JSONEncoder


class Encoder(JSONEncoder):
    # TODO add documentation
    def default(self, o):
        if "to_json" in dir(o):
            return o.to_json()
        return JSONEncoder.default(self, o)


class VerboseEncoder(JSONEncoder):
    def default(self, o):
        # Uses verbose variant, if it does not exist, uses normal to_json
        if "to_json_verbose" in dir(o):
            return o.to_json_verbose()
        elif "to_json" in dir(o):
            return o.to_json()
        return JSONEncoder.default(self, o)


class JsonOutput:
    @staticmethod
    def json_export(host_list, verbose, file_path):
        with open(file_path, "w") as writer:
            if verbose:
                writer.write(dumps(host_list, indent=4, cls=VerboseEncoder))
            else:
                writer.write(dumps(host_list, indent=4, cls=Encoder))
