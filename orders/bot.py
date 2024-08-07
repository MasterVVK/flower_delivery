import json
import os
import logging
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.client.session.aiohttp import AiohttpSession

# Добавление корневой директории проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Установка переменной окружения для настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flower_delivery.settings')
import django
django.setup()

# Импорт моделей после настройки Django
from orders.models import Product, Order, OrderProduct

# Чтение конфигурационного файла
with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')) as config_file:
    config = json.load(config_file)

API_TOKEN = config['telegram_token']
WEBHOOK_HOST = config['webhook_url']
WEBHOOK_PATH = '/webhook/'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
CHAT_ID = config['chat_id']

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN, session=AiohttpSession())
dp = Dispatcher(bot)

# Обработчики команд
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Я бот для управления заказами.")

@dp.message_handler(commands=['catalog'])
async def send_catalog(message: types.Message):
    products = Product.objects.all()
    response = "Каталог продуктов:\n"
    for product in products:
        response += f"{product.name} - {product.price} руб.\n"
    await message.reply(response)

# Настройка вебхуков
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app):
    await bot.delete_webhook()

# Обработчик вебхуков
async def handle_webhook(request):
    update = types.Update(**await request.json())
    await dp.process_update(update)
    return web.Response()

# Инициализация aiohttp
app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle_webhook)
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

# Запуск сервера
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)
