import json
import os
import logging
from aiogram import Bot
from asgiref.sync import sync_to_async

# Загрузка конфигурации
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
if not os.path.exists(config_path):
    raise FileNotFoundError(f"Файл конфигурации не найден: {config_path}")

with open(config_path) as config_file:
    config = json.load(config_file)

API_TOKEN = config['telegram_token']
CHAT_ID = config['chat_id']

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)

async def notify_new_order(order):
    message = await sync_to_async(construct_order_message)(order)
    await bot.send_message(chat_id=CHAT_ID, text=message)

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
