import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TickerConsumer(AsyncWebsocketConsumer):
    group_name = "frontpage"

    async def connect(self):
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def push_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))
