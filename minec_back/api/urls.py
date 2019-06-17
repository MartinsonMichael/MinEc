from django.conf.urls import url
from . import ask_dict_sender, apps
from .views import index
from api.get_updates_dates import get_as_table

urlpatterns = [
    url(r'^control/(?P<func>\S+)?', index, name='base_control'),
    url(r'^get_ask_dict$', ask_dict_sender.get_ask_dict, name='api_ask_dict'),
    url(r'^get_updates_dates$', get_as_table, name='update_dates'),
    url(r'^get/file/', apps.sent_q_as_file, name='api_file'),
    url(r'^get', apps.perform_api, name='api'),
]
