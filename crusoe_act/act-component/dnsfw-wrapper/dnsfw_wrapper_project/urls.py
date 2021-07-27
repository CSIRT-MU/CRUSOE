from django.urls import path, re_path

import dnsfw_wrapper_project.views as views

urlpatterns = [
    path('health', views.DnsHealthCheck.as_view(), name="health_check"),
    path('capacity', views.DnsCapacity.as_view(), name="capacity"),
    path('rules', views.DnsRulesList.as_view(), name="rules"),
    re_path(r'^rules/(?P<ruleId>([1-9])+)$', views.DnsRulesId.as_view(), name="rules_id"),
    re_path(
        r'^(?P<domain>(^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*'
        r'([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])))$',
        views.DnsRuleDomain.as_view(), name="rules_domain")
]
