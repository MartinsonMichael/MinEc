from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<func>\S+)?', views.index, name='control_index'),
]