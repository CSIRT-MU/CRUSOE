class Perspectives:
    def __init__(self, client):
        self.client = client

    def all(self):
        resource = "/perspectives"
        return self.client.get(resource)

    def name_to_id(self, name):
        """
        Obtain all perspectives and then seek for ID of perspective with the given name.
        ValueError is thrown when there is no perspective with the given name.
        :param name:
        :return: respective ID
        """
        perspectives = self.all()
        for perspective in perspectives:
            if perspective['name'] == name:
                return perspective['id']
        raise ValueError("Perspective with name '{}' doesn't exist.".format(name))
