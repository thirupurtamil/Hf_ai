import json
from channels.generic.websocket import AsyncWebsocketConsumer
import asyncio

class LiveDataConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        asyncio.create_task(self.send_data())

    async def disconnect(self, close_code):
        print("Client disconnected", close_code)

    async def send_data(self):
        count = 1
        while True:
            data = {
                "nifty": 19800 + count,
                "volume": 1200 + (count * 10),
            }
            await self.send(text_data=json.dumps(data))
            count += 1
            await asyncio.sleep(3)  # send every 3 sec