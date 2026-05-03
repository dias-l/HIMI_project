"""
ASGI config for HIMI_project project.
Mis à jour pour supporter Django Channels (WebSockets VoIP).
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from gestion.routing import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HIMI_project.settings")

application = ProtocolTypeRouter(
    {
        # Requêtes HTTP classiques Django
        "http": get_asgi_application(),

        # Connexions WebSocket pour la signalisation VoIP
        "websocket": AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        ),
    }
)