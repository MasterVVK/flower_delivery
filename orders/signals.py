import asyncio
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .bot_utils import notify_new_order  # Импорт функции уведомления из bot_utils.py

@receiver(post_save, sender=Order)
def order_created(sender, instance, created, **kwargs):
    if created:
        # Вызов уведомления о новом заказе
        loop = asyncio.get_event_loop()
        loop.run_until_complete(notify_new_order(instance))
