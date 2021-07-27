class Profiles:

    def __init__(self, client):
        self.client = client

    def all(self):
        resource = "/profiles"
        return self.client.get(resource)
