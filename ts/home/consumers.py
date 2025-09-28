import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LiveDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("live_data", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("live_data", self.channel_name)

    async def send_live_data(self, event):
        message = event["message"]
        await self.send(text_data=json.dumps(message))