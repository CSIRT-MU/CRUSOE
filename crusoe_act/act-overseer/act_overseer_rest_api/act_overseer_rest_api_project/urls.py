from django.conf.urls import url

import act_overseer_rest_api_project.views as views

urlpatterns = [
    url(r'^protect_missions_assets$', views.ProtectMissionsAssets.as_view(), name="pma"),
    url(r'^treshold$', views.SecurityTreshold.as_view(), name="treshold"),
    url(r'^log$', views.Log.as_view(), name="log")
]
