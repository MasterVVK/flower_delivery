import json
import os
import logging
import sys
from contextlib import asynccontextmanager

import django
from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

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

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Настройка вебхуков
@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_webhook(url=WEBHOOK_URL, allowed_updates=dp.resolve_used_update_types(), drop_pending_updates=True)
    yield
    await bot.delete_webhook()

# Инициализация FastAPI
app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Обработчики команд
@dp.message(CommandStart())
async def start(message: types.Message) -> None:
    await message.answer("Привет! Я бот для управления заказами.")

@dp.message(F.text == '/catalog')
async def send_catalog(message: types.Message):
    products = Product.objects.all()
    response = "Каталог продуктов:\n"
    for product in products:
        response += f"{product.name} - {product.price} руб.\n"
    await message.reply(response)

# Обработчик вебхуков
@app.post("/webhook")
async def webhook(request: Request) -> None:
    update = types.Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)

# Основная страница
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Запуск приложения
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
