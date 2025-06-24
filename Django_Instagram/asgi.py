import os

from django.core.asgi import get_asgi_application

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Django_Instagram.settings')

# This needs to be called to initialize Django's settings and app registry.
django_asgi_app = get_asgi_application()

# Now we can import things that depend on Django's setup.
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import directs.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            directs.routing.websocket_urlpatterns
        )
    ),
})