import json
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from channels.generic.websocket import WebsocketConsumer
from .models import ChatGroup, GroupMessage


class ChatRoomConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        self.chatroom_name = self.scope["url_route"]["kwargs"]["chatroom_name"]
        self.chatroom = get_object_or_404(ChatGroup, group_name=self.chatroom_name)
        self.accept()

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        body = text_data_json["body"]

        message = GroupMessage.objects.create(
            body=body,
            author=self.user,
            group=self.chatroom,
        )
        context = {"message": message, "user": self.user}
        html = render_to_string("rtchat/partials/chat_message_p.html", context=context)
        self.send(text_data=html)
