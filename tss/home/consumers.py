import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .tasks import fur_list, opc_list, acb_list, mkt_list, push_nifty_live


# ------------------ Futures ------------------
class FuturesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.task = asyncio.create_task(self.send_futures_loop())

    async def disconnect(self, close_code):
        if hasattr(self, "task"):
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

    async def send_futures_loop(self):
        try:
            while True:
                data = await sync_to_async(fur_list)()
                await self.send(text_data=json.dumps({"futures": data}))
                await asyncio.sleep(30)
        except asyncio.CancelledError:
            pass

# ------------------ Options ------------------
class OptionsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.task = asyncio.create_task(self.send_options_loop())

    async def disconnect(self, close_code):
        if hasattr(self, "task"):
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

    async def send_options_loop(self):
        try:
            while True:
                raw_data = await sync_to_async(opc_list)()
                await self.send(text_data=json.dumps({"options": raw_data}))
                await asyncio.sleep(30)
        except asyncio.CancelledError:
            pass

# ------------------ Contracts ------------------
class ContractsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.task = asyncio.create_task(self.send_contracts_loop())

    async def disconnect(self, close_code):
        if hasattr(self, "task"):
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

    async def send_contracts_loop(self):
        try:
            while True:
                data = await sync_to_async(acb_list)()
                await self.send(text_data=json.dumps({"contracts": data}))
                await asyncio.sleep(30)
        except asyncio.CancelledError:
            pass

# ------------------ Market ------------------
class MarketConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.task = asyncio.create_task(self.send_market_loop())

    async def disconnect(self, close_code):
        if hasattr(self, "task"):
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

    async def send_market_loop(self):
        try:
            while True:
                data = await sync_to_async(mkt_list)()
                await self.send(text_data=json.dumps({"market": data}))
                await asyncio.sleep(30)
        except asyncio.CancelledError:
            pass






class NiftyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("nifty_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("nifty_group", self.channel_name)

    async def nifty_update(self, event):
        await self.send(text_data=json.dumps(event['data']))





