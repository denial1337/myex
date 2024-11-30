from django.urls import re_path
from . import consumers
from .models import MAX_TICKER_LENGTH

websocket_urlpatterns = [
    re_path(r'ws/$', consumers.MyConsumer.as_asgi()),
]