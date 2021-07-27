class Events:
    def __init__(self, client):
        self.client = client

    def detail(self, event_id, targets=True):
        resource = f"/event/{event_id}"
        return self.client.get(resource, params={'targets': int(targets)})

    def search(self,
               # Mandatory params
               from_timestamp,
               to_timestamp,
               # Request params
               asynchronous=None,
               count=None,
               limit=None,
               offset=None,
               orderBy=None,
               # Search object params
               source=None,
               target=None,
               event_type=None,
               filter=None,
               nfSource=None,
               perspective=None,
               priority=None):

        """
        Search for events. Parameters are same as mentioned in Developer Guide with a few changes.

        :param from_timestamp: string or datetime. Microseconds are erased when datetime object is passed, because
                                Flowmon API doesn't accept timestamps with microseconds.
        :param to_timestamp: same as from_timestamp
        :param asynchronous:
        :param count:
        :param limit: Beware! Flowmon API has default limit (500).
        :param offset:
        :param orderBy:
        :param source:
        :param target:
        :param event_type:
        :param filter:
        :param nfSource:
        :param perspective: Works with ID or name of perspective.
        :param priority:
        :return: list of events
        """

        resource = "/events"

        # Get perspective ID
        if perspective is None:
            perspective_id = None
        else:
            try:
                perspective_id = int(perspective)
            except ValueError:
                if isinstance(perspective, str):
                    perspective_id = self.client.perspectives.name_to_id(perspective)
                else:
                    raise ValueError("Invalid value for perspective: '{}'. It's not an valid ID or name of existing "
                                     "perspective.".format(perspective))

        search_object = {
            'from': str(Events._round_datetime(from_timestamp)),
            'to': str(Events._round_datetime(to_timestamp)),
            'source': source,
            'target': target,
            'type': event_type,
            'filter': filter,
            'nfSource': nfSource,
            'perspective': perspective_id,
            'priority': priority,
        }

        params = {
            'limit': limit,
            'offset': offset,
            'async': asynchronous,
            'count': count,
            'orderBy': orderBy,
            'search': search_object,
        }
        return self.client.get(resource, params=params)

    @staticmethod
    def _round_datetime(d):
        import datetime
        if isinstance(d, datetime.datetime):
            return d.replace(microsecond=0)
        return d
