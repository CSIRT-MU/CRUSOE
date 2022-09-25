import logging
from json import load, dumps
from os.path import exists

from django.http import JsonResponse
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view

from recommender.neo4j_client import Neo4jClient
from recommender.recommender import Recommender
from utils.json_encoder import Encoder
from utils.mean_bound_calculator import MeanBoundCalculator
from utils.validator import Validator


def get_logger():
    """
    Initializes logger for logging in file recommender.log.
    :return: Initialized logger
    """
    logger = logging.getLogger("neo4j")
    logger.setLevel(20)
    file_handler = logging.FileHandler("recommender.log")
    log_format = "[%(levelname)s] - %(asctime)s - %(name)s - : %(message)s"
    file_handler.setFormatter(logging.Formatter(log_format))
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    return logger


def get_db_client():
    """
    Returns new Neo4j client initialized with connection details from Django's
    settings.
    :return: Neo4j client
    """
    return Neo4jClient(settings.DATABASES['default']['URL'],
                       settings.DATABASES['default']['USER'],
                       settings.DATABASES['default']['PASSWORD'],
                       get_logger())


def initialize_recommender(ip, domain, db_client):
    """
    Initializes recommender object for use in views. IP or domain must be
    given.
    :param ip: IP of attacked host
    :param domain: Domain of attacked host
    :param db_client: Neo4j database client
    :return: Initialized recommender
    """
    with open(settings.CONFIG, 'r') as config_stream:
        config = load(config_stream)

    recommend = Recommender(config, db_client, get_logger())

    if ip is not None:
        recommend.get_attacked_host_by_ip(ip)
    else:
        recommend.get_attacked_host_by_ip(domain)

    return recommend


def parse_query_params(query_params):
    """
    Parses query parameters for recommender endpoints (IP or domain name).
    :param query_params: Dict of query params from REST framework Request
    :return: Tuple of IP and domain (one can be None).
    """
    if "ip" not in query_params and "domain" not in query_params:
        raise ValueError("IP or domain parameter is required.")

    if "ip" in query_params and not Validator.validate_ip(query_params["ip"]):
        raise ValueError("Invalid IP.")

    if "domain" in query_params \
            and not Validator.validate_ip(query_params["domain"]):
        raise ValueError("Invalid domain.")

    return query_params.get("ip", None), query_params.get("domain", None)


@api_view(["GET"])
def attacked_host(request):
    """
    View for obtaining information about attacked host. Requires IP or domain
    of attacked host as a query parameter.
    :param request: REST framework request
    :return:
    """
    with get_db_client() as db_client:
        try:
            ip, domain = parse_query_params(request.query_params)
            recommend = initialize_recommender(ip, domain, db_client)
        except (ValueError, IOError) as e:
            return JsonResponse({"error": {"message": str(e)}}, status=400)

    return JsonResponse(recommend.attacked_host, safe=False, encoder=Encoder)


@api_view(["GET"])
def recommended_hosts(request):
    """
    View for recommending similar hosts. Requires IP or domain of attacked
    host as a query parameter.
    :param request: REST framework request
    :return: JsonResponse containing recommended hosts in JSON
    """
    with get_db_client() as db_client:
        try:
            ip, domain = parse_query_params(request.query_params)
            recommend = initialize_recommender(ip, domain, db_client)
        except (ValueError, IOError) as e:
            return JsonResponse({"error": {"message": str(e)}}, status=400)

        recommend.recommend_hosts()

    return JsonResponse(recommend.host_list, safe=False, encoder=Encoder)


@api_view(["GET", "PUT", "PATCH"])
def configuration(request):
    """
    View for getting and updating recommender configuration file.
    :param request: REST framework request
    :return: Response or JsonResponse for GET method, Response for PUT method,
    Response for PATCH method
    """
    if request.method == "GET":
        if not exists(settings.CONFIG):
            return Response(status=404)

        with open(settings.CONFIG, 'r') as config_stream:
            config = load(config_stream)

        return JsonResponse(config, status=200)

    if request.method == "PUT":
        status_code = 201 if not exists(settings.CONFIG) else 200

        with open(settings.CONFIG, "w") as writer:
            writer.write(dumps(request.data, indent=4))

        return JsonResponse(status=status_code)

    if request.method == "PATCH":
        if not exists(settings.CONFIG):
            return Response(status=404)

        with open(settings.CONFIG, 'r') as config_stream:
            config = load(config_stream)

        with get_db_client() as db_client:
            MeanBoundCalculator.calculate_mean_bounds(db_client, config)

        with open(settings.CONFIG, "w") as writer:
            writer.write(dumps(config, indent=4))

        return JsonResponse(config, status=200)

    return Response(status=500)
