from django.conf.urls import url
from django.contrib.auth import views

from .views import *


urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^accounts/login/$', views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^accounts/logout/$', views.logout, {'next_page': 'login'}, name='logout'),
    url(r'^accounts/signup/$', signup, name='signup'),
]
