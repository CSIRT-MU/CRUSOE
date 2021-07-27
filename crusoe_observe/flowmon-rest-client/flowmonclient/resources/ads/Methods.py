class Methods:

    def __init__(self, client):
        self.client = client

    def all(self):
        resource = "/methods"
        return self.client.get(resource)
