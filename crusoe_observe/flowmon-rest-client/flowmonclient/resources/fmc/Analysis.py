class Analysis:
    def __init__(self, client):
        self.client = client
        self.resource = "/analysis"

    def flows(self,
              # Mandatory params
              from_timestamp,
              to_timestamp,
              profile,
              channels,
              output,
              # Request params
              showonly=None,
              # Search object (FlowsListingAnalysisSearch) params
              listing=None,
              filter=None):
        """
        Search for flows. Parameters are same as mentioned in Developer Guide.
        :param from_timestamp:
        :param to_timestamp:
        :param profile:
        :param channels:
        :param output:
        :param showonly:
        :param listing:
        :param filter:
        :return:
        """

        resource = f"{self.resource}/flows"

        search_object = {
            'from': str(from_timestamp),
            'to': str(to_timestamp),
            'profile': profile,
            'channels': channels,
            'listing': listing,
            'filter': filter,
        }

        params = {
            'search': search_object,
            'showonly': showonly,
            'output': output,
        }
        return self.client.get(resource, params=params)

    def chart(self,
              # Mandatory params
              from_timestamp,
              to_timestamp,
              profile,
              chart,
              # Request parameter
              showonly=None):
        """
        Search for flows. Parameters are same as mentioned in Developer Guide.
        :param from_timestamp:
        :param to_timestamp:
        :param profile:
        :param chart:
        :param showonly:
        :param listing:
        :param filter:
        :return:
        """

        resource = f"{self.resource}/chart"

        search_object = {
            'from': str(from_timestamp),
            'to': str(to_timestamp),
            'profile': profile,
            'chart': chart,
        }

        params = {
            'search': search_object,
            'showonly': showonly,
        }
        return self.client.get(resource, params=params)

    def flows_wait(self, *args, **kwargs):
        """ Actively wait for flows results and then return the results. """
        res_id = self.flows(*args, **kwargs)['id']
        return self.client.wait_for_async_results(self.results, res_id)

    def results(self, result_id):
        """ Get results of asynchronous request. None is returned when results are not ready yet. """
        resource = f"{self.resource}/results/{result_id}"
        return self.client.get_async_results(resource)

    def results_all(self):
        resource = f"{self.resource}/results"
        return self.client.get(resource)
