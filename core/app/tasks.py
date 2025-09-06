from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import random

@shared_task
def push_bar_snapshot():
    labels = [f"{i*50}/Call Option" if i % 2 == 0 else f"{i*50}/Put Option" for i in range(1, 15)]
    values = [random.randint(100, 1000) for _ in range(14)]
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "frontpage",
        {"type": "push_update", "data": {"labels": labels, "values": values}}
    )
    return True
