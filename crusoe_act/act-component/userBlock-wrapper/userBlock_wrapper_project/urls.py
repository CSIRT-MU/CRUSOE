from django.urls import path, re_path

import userBlock_wrapper_project.views as views

urlpatterns = [
    path('health', views.UserBlockHealthCheck.as_view(), name="health_check"),
    path('capacity', views.UserBlockCapacity.as_view(), name="capacity"),
    path('blocked', views.UserBlockBlockedList.as_view(), name="blocked"),
    re_path(r'^blocked/(?P<ruleId>([1-9])+)$', views.UserBlockBlockedRuleId.as_view(), name="rules_id"),
    re_path(r'^(?P<user>(\w+))$', views.UserBlockUser.as_view(), name="user")
]
