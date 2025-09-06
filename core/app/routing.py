from django.urls import re_path
from .consumers import TickerConsumer

websocket_urlpatterns = [
    re_path(r"^ws/ticker/$", TickerConsumer.as_asgi()),
]
