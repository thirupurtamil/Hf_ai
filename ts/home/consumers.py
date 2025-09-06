# home/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LiveDataConsumer(AsyncWebsocketConsumer):
    GROUP_NAME = "live_data_group"

    async def connect(self):
        await self.channel_layer.group_add(self.GROUP_NAME, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP_NAME, self.channel_name)

    # receive messages from group (sent by Celery via channel layer)
    async def live_data_message(self, event):
        # event expected to carry 'text' JSON string
        await self.send(text_data=event["text"])