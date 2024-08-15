# Удалим вызов notify_new_order из signals.py
# Так как теперь мы вызываем notify_new_order непосредственно после создания заказа и добавления продуктов в views.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order

@receiver(post_save, sender=Order)
def order_created(sender, instance, created, **kwargs):
    pass  # Убираем вызов notify_new_order
