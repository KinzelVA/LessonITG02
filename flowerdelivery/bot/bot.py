import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from config import BOT_TOKEN, API_URL  # Убедитесь, что у вас есть токен бота
import requests
import asyncio
import aiohttp



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Добро пожаловать в FlowerDelivery! Вы можете делать заказы через этот бот.")

@dp.message(Command('new_order'))
async def new_order(message: Message):
    await message.answer("Введите ID заказа для подтверждения.")

@dp.message(lambda message: message.text.isdigit())
async def handle_order_id(message: Message):
    order_id = message.text
    # Имитация запроса к веб-приложению для получения данных о заказе
    response = requests.get(f"http://localhost:http://127.0.0.1:8000/api/orders/{order_id}/")
    if response.status_code == 200:
        order_data = response.json()
        await message.answer(f"Ваш заказ: {order_data}")
    else:
        await message.answer("Заказ не найден.")

async def get_orders():
    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                return None

async def notify_new_order(order_data):
    bot = Bot(token=BOT_TOKEN)
    message = f"Новый заказ №{order_data['id']} от {order_data['user']}"
    await bot.send_message(chat_id='CHAT_ID', text=message)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


