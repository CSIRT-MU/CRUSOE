from django.urls import path, re_path, include
from . import views

urlpatterns = [

    path('api-auth', include('rest_framework.urls')),
    # PAO
    path('act/initialize', views.init_pao, name='initialize paos'),
    path('act/paos', views.pao, name='paos'),
    re_path(r'act/(?P<pao_name>[^/]+)/liveness$', views.pao_last_contact, name='pao liveliness'),
    re_path(r'act/(?P<pao_name>[^/]+)/maxCapacity', views.pao_max_capacity, name='pao max capacity'),
    re_path(r'act/(?P<pao_name>[^/]+)/usedCapacity', views.pao_used_capacity, name='pao used capacity'),
    re_path(r'act/(?P<pao_name>[^/]+)/freeCapacity', views.pao_free_capacity, name='pao free capacity'),
    re_path(r'act/(?P<pao_name>[^/]+)/status', views.pao_status, name='pao status'),

    # ORANGE LAYER
    path('events', views.events, name='events'),
    re_path(r'^events/after/(?P<date>\d{4}((\/)(((0)[0-9])|((1)[0-2]))((\/)([0-2][0-9]|(3)[0-1]))?)?)',
            views.events_after_date, name='events after date'),
    re_path(r'^events/(?P<date>\d{4}((\/)(((0)[0-9])|((1)[0-2]))((\/)([0-2][0-9]|(3)[0-1]))?)?)',
            views.events_by_date, name='events on date'),

    # RED LAYER
    # not implemented, missing data

    # BLUE LAYER
    path('missions', views.mission, name='missions'),
    path('missions/hosts', views.hosts_for_all_missions, name='Hosts for all missions'),
    re_path(r'missions/(?P<name>[^/]+)$', views.mission_details, name='mission details'),
    re_path(r'mission/(?P<name>[^/]+)/configurations$', views.mission_configurations, name='mission configurations'),
    re_path(r'mission/(?P<name>[^/]+)/hosts$', views.mission_hosts, name='mission hosts'),
    re_path(r'mission/(?P<name>[^/]+)/configuration/(?P<config_id>\d+)/hosts$',
            views.configuration, name='configuration'),

    # PURPLE LAYER
    path('cve', views.cve, name='CVE'),
    re_path(r'^cve/(?P<cve_id>CVE-\d{4}-\d{4,7})$', views.cve_details, name='CVE details'),
    re_path(r'^cve/(?P<cve_id>CVE-\d{4}-\d{4,7})/ips$', views.cve_ips, name='CVE ips'),

    # GREEN LAYER
    path('software', views.software, name='software'),
    re_path(r'^software/(?P<name>[^/]+)/ips', views.software_ips, name='software ips'),
    path('services', views.services, name='services'),
    re_path(r'^services/(?P<name>[^/]+)/ips', views.service_ips, name='service ips'),
    re_path(r'^services/(?P<name>[^/]+)', views.service_details, name='service details'),

    # YELLOW LAYER
    path('org_units', views.org_units, name='organization units'),
    re_path(r'^org_units/(?P<name>[^/]+)/subnets$', views.org_unit_subnets, name='organization unit subnets'),

    #  LIGHT-BLUE LAYER
    path('ip', views.ip, name='IPs'),
    re_path(r'^ip/(?P<address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/cve', views.ip_cve, name='cve related to the IP'),
    re_path(r'^ip/(?P<address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/services',
            views.ip_services, name='services related to the IP'),
    re_path(r'^ip/(?P<address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/software',
            views.ip_software, name='software related to the IP'),
    re_path(r'^ip/(?P<address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/events/(?P<date>\d{4}((\/)(((0)[0-9])|((1)[0-2]))((\/)([0-2][0-9]|(3)[0-1]))?)?)',
            views.ip_events_date, name='events related to the IP by date'),
    re_path(r'^ip/(?P<address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/events/latest',
            views.ip_events_latest, name='latest events related to the IP'),
    re_path(r'^ip/(?P<address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})/events',
            views.ip_events, name='events related to the IP'),
    re_path(r'^ip/(?P<address>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})?', views.ip_details, name='IP details'),
    path('subnets', views.subnet, name='subnets'),
    re_path(r'^subnets/(?P<subnet>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})/ips',
            views.subnet_ips, name='subnet ips'),
    re_path(r'^subnets/(?P<subnet>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\/\d{1,2})?',
            views.subnet_details, name='subnet details'),
]
