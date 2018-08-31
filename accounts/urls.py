from django.conf.urls import url, include
from rest_framework import routers

from .views import *

router = routers.SimpleRouter()
router.register(r'users', UserViewSet)

urlpatterns = (
    url(r'^accounts/(?P<username>[^/]+)/change/$', user_account, name='user_account'),
    url(r'^accounts/profile/(?P<username>[^/]+)/change/$', user_profile, name='user_profile'),
)
