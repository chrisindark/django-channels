from django.conf.urls import url, include
from rest_framework import routers

from .views import *

urlpatterns = [
    # url(r'^$', index),
    # url(r'^$', views.about, name='about'),
    # url(r'^new/$', views.new_room, name='new_room'),
    # url(r'^(?P<label>[\w-]{,50})/$', views.chat_room, name='chat_room'),
    url(r'^thread/direct/(?P<username>[^/]+)/$', thread_direct, name='thread_direct'),
]

router = routers.SimpleRouter()
router.register('api/thread/direct/(?P<username>[^/]+)', MessageViewSet)

urlpatterns += router.urls
