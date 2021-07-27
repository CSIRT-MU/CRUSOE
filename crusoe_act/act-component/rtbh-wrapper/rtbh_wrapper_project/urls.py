from django.urls import path, re_path

import rtbh_wrapper_project.views as views

urlpatterns = [
    path('health', views.RtbhHealthCheck.as_view(), name="health_check"),
    path('capacity', views.RtbhCapacity.as_view(), name="capacity"),
    path('blocked', views.RtbhBlockedList.as_view(), name="blocked"),
    re_path(r'^blocked/(?P<blockedId>([1-9])+)$', views.RtbhBlockedId.as_view(), name="blocked_id"),
    re_path(r'^(?P<blockedIp>([0-9]{1,3}\.){3}[0-9]{1,3})$', views.RtbhBlockedIp.as_view(), name="blocked_ip")
]
