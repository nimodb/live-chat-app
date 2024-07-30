from django.urls import path
from .consumers import ChatRoomConsumer, OnlineStatusConsumer

websocket_urlpatterns = [
    path("ws/chatroom/<chatroom_name>", ChatRoomConsumer.as_asgi()),
    path("ws/online-status/", OnlineStatusConsumer.as_asgi()),
]
