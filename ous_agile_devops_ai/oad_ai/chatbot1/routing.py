# chatbot1/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/documents/(?P<source_name>\w+)/$', consumers.DocumentConsumer.as_asgi()),
]
