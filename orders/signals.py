from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from .bot import notify_new_order
@receiver(post_save, sender=Order)
def send_order_notification(sender, instance, created, kwargs):
  if created:

      notify_new_order(instance)
