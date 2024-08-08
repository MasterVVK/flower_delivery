import json
import os
import logging
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# Настройка путей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Загрузка настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flower_delivery.settings')

# Импорт моделей Django
from orders.models import Product, Order, OrderProduct

# Загрузка конфигурации
config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')
if not os.path.exists(config_path):
    raise FileNotFoundError(f"Файл конфигурации не найден: {config_path}")

with open(config_path) as config_file:
    config = json.load(config_file)

API_TOKEN = config['telegram_token']
WEBHOOK_HOST = config['webhook_url']
WEBHOOK_PATH = '/webhook/'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
CHAT_ID = config['chat_id']

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(F.text == '/start')
async def start(message: types.Message):
    await message.answer("Привет! Я бот для управления заказами. Вы будете получать уведомления о новых заказах.")

# Функция уведомления о новом заказе
async def notify_new_order(order):
    message = f"Новый заказ №{order.id}\nПользователь: {order.user.username}\nСтатус: {order.get_status_display()}\n"
    message += "Продукты:\n"
    for order_product in order.orderproduct_set.all():
        message += f"{order_product.quantity} x {order_product.product.name}\n"
    await bot.send_message(chat_id=CHAT_ID, text=message)

# Обработчик запуска aiohttp
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

# Обработчик остановки aiohttp
async def on_shutdown(app):
    await bot.delete_webhook()

# Настройка приложения aiohttp
app = web.Application()
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

# Регистрация SimpleRequestHandler
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)

# Запуск приложения
if __name__ == '__main__':
    setup_application(app, dp)
    web.run_app(app, host='0.0.0.0', port=5000)
