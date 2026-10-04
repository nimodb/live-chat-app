import json
from django.db.models import Q
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import ChatGroup, GroupMessage


class ChatRoomConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        self.chatroom_name = self.scope["url_route"]["kwargs"]["chatroom_name"]
        self.chatroom = ChatGroup.objects.filter(group_name=self.chatroom_name).first()
        self.joined = False

        # same rules as chat_view: reject before joining the channel group
        if not self.can_access():
            self.close()
            return

        async_to_sync(self.channel_layer.group_add)(
            self.chatroom_name, self.channel_name
        )
        self.joined = True

        # add and update online users
        if self.user not in self.chatroom.users_online.all():
            self.chatroom.users_online.add(self.user)
            self.update_online_count()

        self.accept()

    def can_access(self):
        if self.chatroom is None or not self.user.is_authenticated:
            return False
        if not self.user.emailaddress_set.filter(verified=True).exists():
            return False
        # chat_view adds the visitor to a group chat before the page connects
        if self.chatroom.is_private or self.chatroom.groupchat_name:
            return self.chatroom.members.filter(pk=self.user.pk).exists()
        return True

    def disconnect(self, close_code):
        # also runs after a rejected connect
        if not self.joined:
            return

        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name, self.channel_name
        )

        # remove and update online users
        if self.user in self.chatroom.users_online.all():
            self.chatroom.users_online.remove(self.user)
            self.update_online_count()

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        body = text_data_json["body"]

        message = GroupMessage.objects.create(
            body=body,
            author=self.user,
            group=self.chatroom,
        )
        event = {
            "type": "message_handler",
            "message_id": message.id,
        }
        async_to_sync(self.channel_layer.group_send)(self.chatroom_name, event)

    def message_handler(self, event):
        message_id = event["message_id"]
        message = GroupMessage.objects.get(id=message_id)
        context = {
            "message": message,
            "user": self.user,
            "chat_group": self.chatroom,
        }
        html = render_to_string("rtchat/partials/chat_message_p.html", context=context)
        self.send(text_data=html)

    def update_online_count(self):
        online_count = self.chatroom.users_online.count() - 1
        event = {
            "type": "online_count_handler",
            "online_count": online_count,
        }
        async_to_sync(self.channel_layer.group_send)(self.chatroom_name, event)

    def online_count_handler(self, event):
        online_count = event["online_count"]

        context = {
            "online_count": online_count,
            "chat_group": self.chatroom,
            "users": self.get_chatroom_users(),
            "user": self.user,
        }
        html = render_to_string("rtchat/partials/online_count.html", context=context)
        self.send(text_data=html)

    def get_chatroom_users(self):
        chat_group = ChatGroup.objects.get(group_name=self.chatroom_name)
        chat_messages = chat_group.chat_messages.all()[:30]
        author_ids = set([message.author.id for message in chat_messages])
        return User.objects.filter(id__in=author_ids)


class OnlineStatusConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]
        self.group_name = "online-status"
        self.group = ChatGroup.objects.filter(group_name=self.group_name).first()
        self.joined = False

        if self.group is None or not self.user.is_authenticated:
            self.close()
            return
        self.joined = True

        if self.user not in self.group.users_online.all():
            self.group.users_online.add(self.user)

        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)

        self.accept()
        self.online_status()

    def disconnect(self, code):
        if not self.joined:
            return

        if self.user in self.group.users_online.all():
            self.group.users_online.remove(self.user)

        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )

        self.online_status()

    def online_status(self):
        event = {"type": "online_status_handler"}
        async_to_sync(self.channel_layer.group_send)(self.group_name, event)

    def online_status_handler(self, event):
        context = {
            "online_users": self.get_online_users(),
            "online_in_public_chats": self.is_online_in_public_chat(),
            "online_in_private_chats": self.is_online_in_private_chats(),
            "online_in_group_chats": self.is_online_in_group_chats(),
            "user": self.user,
        }
        html = render_to_string("rtchat/partials/online_status.html", context)
        self.send(text_data=html)

    def get_online_users(self):
        return self.group.users_online.exclude(id=self.user.id)

    def is_online_in_public_chat(self):
        public_chat = ChatGroup.objects.get(
            group_name="public-chat"
        ).users_online.exclude(id=self.user.id)
        if public_chat:
            return True
        return False

    def is_online_in_private_chats(self):
        my_private_chats = self.user.chat_groups.filter(is_private=True)
        return any(
            chat.users_online.exclude(id=self.user.id).exists()
            for chat in my_private_chats
        )

    def is_online_in_group_chats(self):
        my_group_chats = self.user.chat_groups.filter(
            Q(groupchat_name__isnull=False) & ~Q(groupchat_name="")
        )
        return any(
            chat.users_online.exclude(id=self.user.id).exists()
            for chat in my_group_chats
        )
