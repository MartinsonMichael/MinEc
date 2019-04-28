from django.conf.urls import url

from . import apps

urlpatterns = [
    url(r'^', apps.perform_api, name='api'),
]