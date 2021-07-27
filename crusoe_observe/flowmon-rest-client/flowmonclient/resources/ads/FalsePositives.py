class FalsePositives:

    def __init__(self, client):
        self.client = client

    def template(self):
        resource = "/templates/false-positive"
        return self.client.get(resource)

    def all(self):
        resource = "/false-positives"
        return self.client.get(resource)

    def detail(self, false_positive_id):
        resource = f"/false-positives/{false_positive_id}"
        return self.client.get(resource)

    def create(self,
               # Mandatory params
               code,
               source=None,
               target=None,
               # Search object params
               netFlowSources=None,
               sourceFilters=None,
               targetFilters=None,
               days='XX',
               timeFrom=None,
               timeTo=None,
               validTo=None,
               comment=None):
        """
        Create False Positive. Parameters should be generally same as in Developer Guide, but because of poor
        documentation, there is some notes/params which aren't mentioned in the guide.
        :param code:
        :param source:
        :param target:
        :param netFlowSources:
        :param sourceFilters:
        :param targetFilters:
        :param days: default value 'XX' (or also ['XX']) means whole week
        :param timeFrom:
        :param timeTo:
        :param validTo:
        :param comment:
        :return:
        """

        resource = "/false-positives"

        falsePositive = {
            'code': code,
            'source': source,
            'target': target,
            'netFlowSources': netFlowSources,
            'sourceFilters': sourceFilters,
            'targetFilters': targetFilters,
            'days': days,
            'timeFrom': timeFrom,
            'timeTo': timeTo,
            'validTo': validTo,
            'comment': comment,
        }

        return self.client.post(resource, params={'entity': falsePositive})

    def delete(self, false_positive_id):
        resource = f"/false-positives/{false_positive_id}"
        return self.client.delete(resource)
