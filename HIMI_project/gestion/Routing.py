from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/voip/(?P<contact_id>\d+)/$",
        consumers.VoIPConsumer.as_asgi(),
    ),
]