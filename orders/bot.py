import json
import os
import logging
import sys
from datetime import datetime, timedelta
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.dispatcher.webhook import get_new_configured_app
from asgiref.sync import sync_to_async
from django.db.models import Sum, F

# Устанавливаем текущий рабочий каталог на уровень выше, если это не так
current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.dirname(current_path)
sys.path.append(parent_path)

# Загрузка настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flower_delivery.settings')
import django
django.setup()

# Импорт моделей Django
from orders.models import Product, Order, Review

# Загрузка конфигурации
config_path = os.path.join(parent_path, 'config.json')
if not os.path.exists(config_path):
    raise FileNotFoundError(f"Файл конфигурации не найден: {config_path}")

with open(config_path) as config_file:
    config = json.load(config_file)

API_TOKEN = config['telegram_token']
WEBHOOK_HOST = config['webhook_url']
WEBHOOK_PATH = '/webhook/'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: Message):
    await message.answer("Привет! Я бот для управления заказами. Вы будете получать уведомления о новых заказах.\n"
                         "Используйте команды:\n"
                         "/sales_report - Отчет о продажах\n"
                         "/user_activity - Активность пользователей\n"
                         "/product_popularity - Популярность продуктов")

# Команда /sales_report для получения отчета о продажах
@dp.message_handler(commands=['sales_report'])
async def sales_report(message: Message):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    # Используем sync_to_async для обращения к базе данных
    recent_orders = await sync_to_async(lambda: list(Order.objects.filter(created_at__range=[start_date, end_date])))()

    if not recent_orders:
        await message.answer("За последние 7 дней не было сделано ни одного заказа.")
        return

    # Собираем все значения в список, используя list comprehension
    total_sales_list = [
        await sync_to_async(lambda: order.orderproduct_set.aggregate(
            total=Sum(F('quantity') * F('product__price'))
        )['total'])() for order in recent_orders
    ]

    # Теперь используем sum() для суммирования всех значений
    total_sales = sum(total_sales_list)
    total_orders = len(recent_orders)

    report = (f"Отчет о продажах за последние 7 дней:\n"
              f"Общая сумма продаж: {total_sales:.2f} руб.\n"
              f"Количество заказов: {total_orders}\n")

    await message.answer(report)

# Команда /user_activity для получения отчета об активности пользователей
@dp.message_handler(commands=['user_activity'])
async def user_activity(message: Message):
    start_date = datetime.now() - timedelta(days=7)
    recent_reviews = await sync_to_async(lambda: list(Review.objects.filter(created_at__gte=start_date)))()
    total_reviews = len(recent_reviews)

    report = (f"Отчет об активности пользователей за последние 7 дней:\n"
              f"Количество новых отзывов: {total_reviews}\n")

    await message.answer(report)

# Команда /product_popularity для получения отчета о популярности продуктов
@dp.message_handler(commands=['product_popularity'])
async def product_popularity(message: Message):
    popular_products = await sync_to_async(lambda: list(Product.objects.annotate(total_sales=Sum('orderproduct__quantity')).order_by('-total_sales')[:5]))()

    if not popular_products:
        await message.answer("Не удалось найти популярные продукты.")
        return

    report = "Топ 5 популярных продуктов:\n"
    for product in popular_products:
        report += f"{product.name}: {product.total_sales} продано\n"

    await message.answer(report)

# Обработчик запуска aiohttp
async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

# Настройка приложения aiohttp
app = get_new_configured_app(dispatcher=dp, path=WEBHOOK_PATH)
app.on_startup.append(on_startup)

# Запуск приложения
if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=5000)
