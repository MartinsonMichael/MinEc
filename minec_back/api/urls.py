from django.conf.urls import url, include
from . import ask_dict_sender, apps
import base_control

urlpatterns = [
    url(r'^control/', include('base_control.urls')),
    url(r'^get_ask_dict$', ask_dict_sender.get_ask_dict, name='api_ask_dict'),
    url(r'^get/file/', apps.sent_q_as_file, name='api_file'),
    url(r'^get', apps.perform_api, name='api'),
]
