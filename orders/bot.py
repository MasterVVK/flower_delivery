import json
import os
import logging
import django
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from orders.models import Product, Order, OrderProduct

# Установка переменной окружения для настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flower_delivery.settings')
django.setup()

with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.json')) as config_file:
    config = json.load(config_file)

API_TOKEN = config['telegram_token']
WEBHOOK_URL = config['webhook_url']

# Настройка логирования
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage, fsm_strategy=FSMStrategy(user=True))

# Настройка middleware для логирования
dp.update.middleware(logging)

@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer("Привет! Я бот для заказа цветов. Вы можете посмотреть наш каталог и сделать заказ.")

@dp.message(Command("catalog"))
async def send_catalog(message: Message):
    products = Product.objects.all()
    response = "Каталог продуктов:\n"
    for product in products:
        response += f"{product.name} - {product.price} руб.\n"
    await message.answer(response)

@dp.message(Command("order"))
async def create_order(message: Message):
    args = message.text.split()[1:]
    if len(args) != 2:
        await message.answer("Используйте команду в формате /order <product_id> <quantity>")
        return
    product_id, quantity = map(int, args)
    product = Product.objects.get(id=product_id)
    order = Order(user_id=message.from_user.id)
    order.save()
    order_product = OrderProduct(order=order, product=product, quantity=quantity)
    order_product.save()
    await message.answer(f"Заказ на {quantity} x {product.name} успешно создан!")

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
