import json
import os
import logging
import requests

# Настройка путей
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
if not os.path.exists(config_path):
    raise FileNotFoundError(f"Файл конфигурации не найден: {config_path}")

with open(config_path) as config_file:
    config = json.load(config_file)

API_TOKEN = config['telegram_token']
CHAT_ID = config['chat_id']

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

def notify_new_order(order):
    message = construct_order_message(order)
    send_message_to_telegram(message)

def construct_order_message(order):
    message = f"<b>Новый заказ №{order.id}</b>\nПользователь: {order.user.username}\nСтатус: {order.get_status_display()}\n"
    message += "<b>Продукты:</b>\n"
    order_products = order.orderproduct_set.all()
    if order_products.exists():
        for order_product in order_products:
            message += f"{order_product.quantity} x {order_product.product.name}\n"
    else:
        message += "Нет продуктов в заказе.\n"
    return message

def send_message_to_telegram(message):
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP error occurred: {err}")
    except Exception as err:
        logging.error(f"An error occurred: {err}")

def notify_order_cancellation(order):
    message = construct_cancellation_message(order)
    send_message_to_telegram(message)

def construct_cancellation_message(order):
    message = f"<b>Заказ №{order.id} был отменен</b>\n"
    message += f"Пользователь: {order.user.username}\n"
    message += f"Дата заказа: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
    message += "<b>Продукты:</b>\n"
    order_products = order.orderproduct_set.all()
    if order_products.exists():
        for order_product in order_products:
            message += f"{order_product.quantity} x {order_product.product.name}\n"
    else:
        message += "Нет продуктов в заказе.\n"
    return message
