import asyncio
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .bot_utils import notify_new_order  # Импорт функции уведомления из bot_utils.py
from asgiref.sync import sync_to_async


@receiver(post_save, sender=Order)
def order_created(sender, instance, created, **kwargs):
    if created:
        async def send_notification(order):
            await notify_new_order(order)

        loop = None
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            asyncio.run_coroutine_threadsafe(send_notification(instance), loop)
        else:
            loop.run_until_complete(send_notification(instance))
            loop.close()
