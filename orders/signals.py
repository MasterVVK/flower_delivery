import asyncio
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .bot_utils import notify_new_order
from asgiref.sync import sync_to_async
import threading

@receiver(post_save, sender=Order)
def order_created(sender, instance, created, **kwargs):
    if created:
        threading.Thread(target=asyncio.run, args=(send_notification(instance),)).start()

async def send_notification(order):
    await notify_new_order(order)
