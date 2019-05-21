from django.conf.urls import url

from . import apps

urlpatterns = [
    url(r'^get_ask_dict$', apps.get_ask_dict, name='api_ask_dict'),
    url(r'^get', apps.perform_api, name='api'),
]