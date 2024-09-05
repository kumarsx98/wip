# asgi.py
import os
import sys
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from chatbot1 import routing

# Add the project directory to the Python path
#project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#sys.path.insert(0, project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oad_ai.settings')

# Import routing after setting the Python path
#from chatbot1 import routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns
        )
    ),
})
