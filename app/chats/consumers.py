import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from events.models import Event
from django.db.models import Q
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    @database_sync_to_async
    def has_connect_permission(self, user, talk_id):
        return (
            user is not None
            and Event.objects.filter(
                Q(is_published=True)
                & (Q(attendees=user) | Q(talk__speaker=user))
                & Q(talk__id=talk_id)
                & Q(talk__start__lte=timezone.now())
                & Q(talk__end__gte=timezone.now())
            ).exists()
        )

    async def connect(self):
        self.user = self.scope["user"]
        self.talk_id = self.scope["url_route"]["kwargs"]["talk_id"]
        self.group_name = f"talk_{self.talk_id}"

        if not (await self.has_connect_permission(self.user, self.talk_id)):
            await self.close()

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name, self.channel_name
        )

    async def receive(self, text_data):
        message = json.loads(text_data)["message"]
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat_message",
                "username": self.user.username,
                "message": message,
            },
        )

    async def chat_message(self, event):
        await self.send(
            text_data=json.dumps(
                {"username": event["username"], "message": event["message"]}
            )
        )
