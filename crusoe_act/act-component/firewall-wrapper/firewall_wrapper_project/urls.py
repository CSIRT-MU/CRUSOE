from django.urls import path, re_path

import firewall_wrapper_project.views as views

urlpatterns = [
    path('health', views.FwHealthCheck.as_view(), name="health_check"),
    path('capacity', views.FwCapacity.as_view(), name="capacity"),
    path('blocked', views.FwBlockedList.as_view(), name="blocked"),
    re_path(r'^blocked/(?P<blockedId>([1-9])+)$', views.FwBlockedId.as_view(), name="blocked_id"),
    re_path(r'^blocked/(?P<blockedId>([1-9])+)/port$', views.FwBlockedIdPort.as_view(), name="blocked_id_port"),
    re_path(r'^blocked/(?P<blockedId>([1-9])+)/reason$', views.FwBlockedIdReason.as_view(), name="blocked_id_reason"),
    re_path(r'^(?P<blockedIp>([0-9]{1,3}\.){3}[0-9]{1,3})$', views.FwBlockedIp.as_view(), name="blocked_ip"),
    re_path(
        r'^((?P<blockedIp>([0-9]{1,3}\.){3}[0-9]{1,3})/'
        r'(?P<blockedPort>([1-9]|[1-5]?[0-9]{2,4}|6[1-4][0-9]{3}|65[1-4][0-9]{2}|655[1-2][0-9]|6553[1-5])))$',
        views.FwBlockedIpBlockedPort.as_view(), name="blocked_ip_blocked_port")
]
