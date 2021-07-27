import time
from oauthlib.oauth2 import LegacyApplicationClient
from requests import HTTPError
from requests_oauthlib import OAuth2Session
import json


class FlowmonException(Exception):
    """ Raised when Flowmon API returns error. """


def prepare_request(fnc):
    """
    This decorator can be used on http methods of :class:`AbstractClient`.
    Do some preparation before request is made:
        * first positional parameter `resource` (e.g. /foo/bar) is extended to full url (e.g. http://baz.cz/rest/foo/bar)
        * take key parameter 'params' and call :func:`prepare_url_params` on it
    """

    def wrapper(self, resource, *, params=None, **kwargs):
        """
        :param self: object :class:`AbstractClient`
        :param resource:
        :param params:
        :param kwargs:
        :return:
        """
        url = self.endpoint_base + resource
        params = prepare_url_params(params)
        return fnc(self, url, params=params, **kwargs)

    return wrapper


def process_response(fnc):
    """
    This decorator takes response from the fnc and raise exception when there is error status code.
    If there isn't error status code, body of response is considered as json and returned as python dictionary.
    :param fnc:
    :return: Body of response as python dictionary.
    """

    def wrapper(*args, **kwargs):
        response = fnc(*args, **kwargs)

        if response is None:
            return None

        try:
            response.raise_for_status()
        except HTTPError as e:
            if response.text:
                raise FlowmonException(response.json()) from e
            else:
                raise FlowmonException() from e

        # There is returned empty list when response body is empty. It's because of Flowmon REST API design.
        # When Flowmon is asked for list of resources and there are no suitable resources to return, Flowmon returns
        # empty body (suitable would be empty list, maybe in future).
        return response.json() if response.text else []

    return wrapper


class AbstractClient:
    def __init__(self,
                 domain="https://collector2.csirt.muni.cz",
                 username=None,
                 password=None,
                 client_id="invea-tech"):
        """
        AbstractClient handles authentication and provides http connection (session parameter),
        also provides convenient methods for making http requests (get, post, put).
        :param domain: Domain of API endpoint (or base part of endpoint).
        :param username: string
        :param password: string
        :param client_id:
        """
        self.endpoint_base = domain + "/rest"
        self.resource_oauth_token = domain + "/resources/oauth/token"

        self.session = OAuth2Session(client=LegacyApplicationClient(client_id=client_id),
                                     auto_refresh_url=self.resource_oauth_token)

        # Set trusted certificate
        import pkg_resources
        self.session.verify = pkg_resources.resource_filename(__name__, "cert/cert.pem")

        # Authenticate
        self.session.fetch_token(username=username, password=password, client_id=client_id,
                                 token_url=self.resource_oauth_token)

    @prepare_request
    @process_response
    def get(self, resource, *, params=None, **kwargs):
        return self.session.get(resource, params=params, **kwargs)

    @prepare_request
    def _get(self, resource, *, params=None, **kwargs):
        return self.session.get(resource, params=params, **kwargs)

    @prepare_request
    @process_response
    def post(self, resource, *, params=None, **kwargs):
        return self.session.post(resource, params=params, **kwargs)

    @prepare_request
    @process_response
    def put(self, resource, *, params=None, **kwargs):
        return self.session.put(resource, params=params, **kwargs)

    @prepare_request
    @process_response
    def delete(self, resource, **kwargs):
        return self.session.delete(resource, **kwargs)

    @process_response
    def get_async_results(self, resource, *, params=None, **kwargs):
        """ Works same as get() with only difference that None is returned when status code is 202. """
        response = self._get(resource, params=params, **kwargs)
        return None if response.status_code == 202 else response

    @staticmethod
    def wait_for_async_results(get_results_fnc, *args, **kwargs):
        """ Actively waits for non None return value of the given get_results_fnc called with given args and kwargs. """
        result = get_results_fnc(*args, **kwargs)
        while result is None:
            time.sleep(0.5)
            result = get_results_fnc(*args, **kwargs)
        return result


def clean_dict(dictionary):
    """ Remove items with None value in the dictionary and recursively in other nested dictionaries. """
    if not isinstance(dictionary, dict):
        return dictionary
    return {k: clean_dict(v) for k, v in dictionary.items() if v is not None}


def prepare_url_params(dictionary):
    """
    Take dictionary and convert nested dicts (and lists) into strings.
    Dictionary items with None value are removed from the dictionary and also from nested dictionaries.
    :param dictionary: dictionary
    :return: Dictionary without nested dicts and lists (replaced by json representation as strings).
    """
    if not isinstance(dictionary, dict):
        return dictionary

    dictionary = clean_dict(dictionary)

    for k, v in dictionary.items():
        if isinstance(v, (list, dict)):
            dictionary[k] = json.dumps(v)
    return dictionary
