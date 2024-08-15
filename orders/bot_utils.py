import json
import os
import logging
from aiogram import Bot, types
from django.conf import settings


# Загрузка конфигурации
config_path = os.path.join(settings.BASE_DIR, 'config.json')
if not os.path.exists(config_path):
    raise FileNotFoundError(f"Файл конфигурации не найден: {config_path}")

with open(config_path) as config_file:
    config = json.load(config_file)

API_TOKEN = config['telegram_token']
CHAT_ID = config['chat_id']

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)

def notify_new_order(order):
    message = construct_order_message(order)
    send_message_to_telegram(message)

def construct_order_message(order):
    message = f"Новый заказ №{order.id}\nПользователь: {order.user.username}\nСтатус: {order.get_status_display()}\n"
    message += "Продукты:\n"
    order_products = order.orderproduct_set.all()
    if order_products.exists():
        for order_product in order_products:
            message += f"{order_product.quantity} x {order_product.product.name}\n"
    else:
        message += "Нет продуктов в заказе.\n"
    return message

def send_message_to_telegram(message):
    async def send_message():
        await bot.send_message(chat_id=CHAT_ID, text=message)

    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(send_message())
