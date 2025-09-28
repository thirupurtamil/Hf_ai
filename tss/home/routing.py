from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/futures/$", consumers.FuturesConsumer.as_asgi()),
    re_path(r"ws/options/$", consumers.OptionsConsumer.as_asgi()),
    re_path(r"ws/contracts/$", consumers.ContractsConsumer.as_asgi()),
    re_path(r"ws/market/$", consumers.MarketConsumer.as_asgi()),
    re_path(r'ws/nifty/$', consumers.NiftyConsumer.as_asgi()),
]


