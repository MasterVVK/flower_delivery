import json
import os
import logging
import sys
import django
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiohttp import web
from aiogram import Router

# Добавление корневой директории проекта в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Установка переменной окружения для настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flower_delivery.settings')
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

# Инициализация бота, диспетчера и маршрутизатора
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage(), fsm_strategy=FSMStrategy.USER_IN_CHAT)
router = Router()

# Функция для отправки уведомления о новом заказе
async def send_new_order_notification(order):
    message = f"Новый заказ #{order.id} от {order.user.username}:\n"
    for order_product in order.orderproduct_set.all():
        message += f"{order_product.quantity} x {order_product.product.name}\n"
    await bot.send_message(chat_id=CHAT_ID, text=message)

# Обработчики команд
@router.message(F.text == '/start')
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот для управления заказами.")

@router.message(F.text == '/catalog')
async def send_catalog(message: types.Message):
    products = Product.objects.all()
    response = "Каталог продуктов:\n"
    for product in products:
        response += f"{product.name} - {product.price} руб.\n"
    await message.reply(response)

# Настройки вебхука
async def on_startup(app: web.Application):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()

async def handle_webhook(request):
    update = await request.json()
    async with bot:
        await bot.set_current()
        await dp.set_current()
        update = types.Update(**update)
        await dp.process_update(update)
    return web.Response()

# Создание и настройка веб-приложения
app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle_webhook)
app.on_startup.append(lambda app: on_startup(app))
app.on_shutdown.append(lambda app: on_shutdown(app))

# Подключение маршрутизатора к диспетчеру
dp.include_router(router)

# Запуск веб-сервера
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)
