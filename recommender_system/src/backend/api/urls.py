from django.urls import path

from .views import attacked_host, recommended_hosts, configuration

urlpatterns = [
    path('attacked-host', attacked_host),
    path('recommended-hosts', recommended_hosts),
    path('configuration', configuration)
]
