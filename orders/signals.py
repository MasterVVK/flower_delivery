import asyncio
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .bot_utils import notify_new_order
import threading

@receiver(post_save, sender=Order)
def order_created(sender, instance, created, **kwargs):
    if created:
        thread = threading.Thread(target=run_async, args=(notify_new_order(instance),))
        thread.start()

def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)
    loop.close()
