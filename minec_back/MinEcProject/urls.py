from django.conf.urls import url
from dj_project.settings import STATICFILES_DIRS

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
]

print(STATICFILES_DIRS)