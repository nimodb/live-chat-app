from django.urls import path
from .consumers import ChatRoomConsumer

websocket_urlpatterns = [
    path("ws/chatroom/<chatroom_name>", ChatRoomConsumer.as_asgi())
]
