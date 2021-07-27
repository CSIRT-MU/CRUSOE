from django.urls import path, re_path

import mailFilter_wrapper_project.views as views

urlpatterns = [
    path('health', views.MailFilterHealthCheck.as_view(), name="health_check"),
    path('capacity', views.MailFilterCapacity.as_view(), name="capacity"),
    path('blocked', views.MailFilterBlockedList.as_view(), name="blocked"),
    re_path(r'^blocked/(?P<ruleId>([1-9])+)$', views.MailFilterBlockedRuleId.as_view(), name="blocked_id"),
    re_path(r'^(?P<ruleAddress>[a-z0-9!#$%&\'*+/=?^_‘{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_‘{|}~-]+)*@'
            r'(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)$',
            views.MailFilterRuleAddress.as_view(), name="rule_address"),
    path('from', views.MailFilterFrom.as_view(), name="from"),
    path('to', views.MailFilterTo.as_view(), name="to")
]
