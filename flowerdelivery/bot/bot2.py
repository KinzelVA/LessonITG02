import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton
from config import BOT_TOKEN  # Убедитесь, что у вас есть токен бота
import aiohttp
import asyncio

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Создание кнопок для клавиатуры
def create_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Каталог цветов")],
            [KeyboardButton(text="Оформить заказ")],
            [KeyboardButton(text="Мои заказы")],
            [KeyboardButton(text="Регистрация")]
        ],
        resize_keyboard=True
    )

# Функция для регистрации пользователя через API
async def register_user_via_bot(username):
    url = "http://127.0.0.1:8000/users/register/"
    data = {'username': username}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return response.status == 201  # Успешная регистрация

# Функция для получения каталога цветов с сайта
async def get_flower_catalog():
    url = "http://127.0.0.1:8000/api/flowers/"  # API для получения списка цветов
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()  # Возвращает список цветов
                else:
                    logging.error(f"Ошибка загрузки каталога. Код ответа: {response.status}")
                    return None
    except Exception as e:
        logging.error(f"Ошибка при запросе каталога: {str(e)}")
        return None

# Функция для оформления заказа через API
async def place_order_via_bot(username, flower_id):
    url = f"http://127.0.0.1:8000/api/orders/"
    data = {'username': username, 'flower_id': flower_id}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return response.status == 201  # Успешное создание заказа

# Команда /start, приветствие и меню
@dp.message(CommandStart())
async def start(message: Message):
    keyboard = create_keyboard()  # Создаем клавиатуру
    await message.answer("Добро пожаловать в FlowerDelivery! Вы можете делать заказы через этот бот.", reply_markup=keyboard)

# Обработка команды "Регистрация"
@dp.message(lambda message: message.text == "Регистрация")
async def register(message: Message):
    username = message.from_user.username or message.from_user.full_name
    registration_success = await register_user_via_bot(username)

    if registration_success:
        await message.answer("Вы успешно зарегистрированы!")
    else:
        await message.answer("Произошла ошибка при регистрации.")

# Обработка команды "Каталог цветов"
@dp.message(lambda message: message.text == "Каталог цветов")
async def show_flower_catalog(message: Message):
    flowers = await get_flower_catalog()

    if flowers:
        # Создаем инлайн-клавиатуру с цветами
        keyboard = InlineKeyboardMarkup(row_width=2)
        for flower in flowers:
            button = InlineKeyboardButton(text=f"{flower['name']} - {flower['price']} руб.", callback_data=f"flower_{flower['id']}")
            keyboard.add(button)

        await message.answer("Выберите цветок для заказа:", reply_markup=keyboard)
    else:
        await message.answer("Не удалось загрузить каталог цветов.")

# Обработка выбора цветка из инлайн-кнопок
@dp.callback_query(lambda c: c.data.startswith('flower_'))
async def handle_flower_selection(callback_query: CallbackQuery):
    flower_id = callback_query.data.split('_')[1]
    username = callback_query.from_user.username or callback_query.from_user.full_name

    # Оформление заказа
    order_success = await place_order_via_bot(username=username, flower_id=flower_id)

    if order_success:
        await callback_query.message.answer("Ваш заказ успешно оформлен!")
    else:
        await callback_query.message.answer("Произошла ошибка при оформлении заказа.")

    # Удаление сообщения с кнопками после оформления заказа
    await callback_query.message.delete()

# Обработка команды "Оформить заказ"
@dp.message(lambda message: message.text == "Оформить заказ")
async def order(message: Message):
    await message.answer("Чтобы оформить заказ, выберите цветок из каталога с помощью команды 'Каталог цветов'.")

# Обработка команды "Мои заказы"
@dp.message(lambda message: message.text == "Мои заказы")
async def my_orders(message: Message):
    username = message.from_user.username or message.from_user.full_name
    url = f"http://127.0.0.1:8000/api/orders/?username={username}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                orders = await response.json()
                if orders:
                    order_list = "\n".join([f"Заказ №{order['id']}: {order['flower_name']} - {order['status']}" for order in orders])
                    await message.answer(f"Ваши заказы:\n{order_list}")
                else:
                    await message.answer("У вас нет заказов.")
            else:
                await message.answer("Не удалось загрузить ваши заказы.")

# Основная функция для запуска бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
