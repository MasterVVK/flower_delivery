import json
import os
import logging
import sys
import datetime
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from datetime import timedelta

# Устанавливаем текущий рабочий каталог на уровень выше, если это не так
current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.dirname(current_path)
sys.path.append(parent_path)

# Загрузка настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flower_delivery.settings')
import django
django.setup()

# Импорт моделей Django
from orders.models import Product, Order, OrderProduct

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

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher()  # Создаем диспетчер без аргументов

# Добавляем бота в диспетчер
dp['bot'] = bot

# Обработчик команды /start
@dp.message(F.text == '/start')
async def start(message: types.Message):
    await message.answer("Привет! Я бот для управления заказами. Вы будете получать уведомления о новых заказах.\n"
                         "Используйте команды:\n"
                         "/sales_report - Отчет о продажах\n"
                         "/user_activity - Активность пользователей\n"
                         "/product_popularity - Популярность продуктов")

# Команда /sales_report для получения отчета о продажах
@dp.message(F.text == '/sales_report')
async def sales_report(message: types.Message):
    # Рассчитываем даты для отчета за последние 7 дней
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    # Получаем заказы за последние 7 дней
    recent_orders = Order.objects.filter(created_at__range=[start_date, end_date])

    if not recent_orders.exists():
        await message.answer("За последние 7 дней не было сделано ни одного заказа.")
        return

    total_sales = sum(order.orderproduct_set.aggregate(sum('quantity') * sum('product__price'))['sum'] for order in recent_orders)
    total_orders = recent_orders.count()

    report = (f"Отчет о продажах за последние 7 дней:\n"
              f"Общая сумма продаж: {total_sales:.2f} руб.\n"
              f"Количество заказов: {total_orders}\n")

    await message.answer(report)

# Команда /user_activity для получения отчета об активности пользователей
@dp.message(F.text == '/user_activity')
async def user_activity(message: types.Message):
    # Вычисляем количество новых отзывов за последние 7 дней
    start_date = datetime.now() - timedelta(days=7)
    recent_reviews = Review.objects.filter(created_at__gte=start_date)
    total_reviews = recent_reviews.count()

    report = (f"Отчет об активности пользователей за последние 7 дней:\n"
              f"Количество новых отзывов: {total_reviews}\n")

    await message.answer(report)

# Команда /product_popularity для получения отчета о популярности продуктов
@dp.message(F.text == '/product_popularity')
async def product_popularity(message: types.Message):
    # Получаем продукты, отсортированные по количеству продаж за все время
    popular_products = Product.objects.annotate(total_sales=Sum('orderproduct__quantity')).order_by('-total_sales')[:5]

    if not popular_products.exists():
        await message.answer("Не удалось найти популярные продукты.")
        return

    report = "Топ 5 популярных продуктов:\n"
    for product in popular_products:
        report += f"{product.name}: {product.total_sales} продано\n"

    await message.answer(report)

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
