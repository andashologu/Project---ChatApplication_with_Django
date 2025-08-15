import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import path
from chatapp.consumer import ChatConsumer

# Set Django settings before importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_project.settings')
django.setup()  # ensures apps are loaded before using models

# WebSocket URL routing
websocket_urlpatterns = [
    path('ws/chat/<int:user_id>/', ChatConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
