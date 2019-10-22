from django.conf.urls import url

from api import app

urlpatterns = [
    # url(r'^control/(?P<func>\S+)?', index, name='base_control'),
    url(r'^get_ask_dict$', app.get_ask_dict, name='api_ask_dict'),
    # url(r'^get_updates_dates$', get_as_table, name='update_dates'),
    # url(r'^get/file/', apps.sent_q_as_file, name='api_file'),
    # url(r'^get/single/', apps.download_table_by_date, name='single_KOSLYL'),
    url(r'^get', app.perform_api, name='api'),
]
