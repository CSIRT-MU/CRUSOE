class Filters:
  
    def __init__(self, client):
        self.client = client

    def all(self):
        resource = "/filters"
        return self.client.get(resource)

