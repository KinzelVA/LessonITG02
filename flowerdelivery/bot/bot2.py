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
# Функция для получения каталога цветов с сайта
async def get_flower_catalog():
    url = "http://127.0.0.1:8000/shop/api/flowers/"  # API для получения списка цветов
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                logging.info(f"Ответ от API: {response.status}")
                response_text = await response.text()
                logging.info(f"Ответ JSON: {response_text}")  # Логирование полного текста ответа

                if response.status == 200:
                    return await response.json()  # Возвращает список цветов
                else:
                    logging.error(f"Ошибка загрузки каталога. Код ответа: {response.status}")
                    return None
    except Exception as e:
        logging.error(f"Ошибка при запросе каталога: {str(e)}")
        return None


# Функция для оформления заказа через API

async def get_user_id_by_username(username):
    url = f"http://127.0.0.1:8000/api/api/users/?username={username}"  # Убедитесь, что URL корректный
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    users = await response.json()
                    logging.info(f"Получен ответ от API: {users}")  # Логируем ответ
                    if users:
                        return users[0]['id']  # Проверяем, что данные пользователя есть
                    else:
                        logging.error(f"Пользователь с именем {username} не найден")
                        return None
                else:
                    logging.error(f"Ошибка при получении ID пользователя. Код ответа: {response.status}")
                    return None
    except Exception as e:
        logging.error(f"Ошибка при запросе ID пользователя: {str(e)}")
        return None

async def place_order_via_bot(user_id, flower_id):
    url = "http://127.0.0.1:8000/orders/api/orders/"
    data = {'user': user_id, 'flowers': [flower_id]}  # flowers должен быть списком
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status == 201:
                    return True
                else:
                    error_json = await response.json()
                    logging.error(
                        f"Ошибка при оформлении заказа. Код ответа: {response.status}, Ответ: {error_json}")
                    return False
    except Exception as e:
        logging.error(f"Ошибка при оформлении заказа: {str(e)}")
        return False


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
        inline_keyboard = []
        for flower in flowers:
            button = InlineKeyboardButton(
                text=f"{flower['name']} - {flower['price']} руб.",
                callback_data=f"flower_{flower['id']}"
            )
            inline_keyboard.append([button])  # Добавляем каждую кнопку в список как отдельный ряд

        keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

        await message.answer("Выберите цветок для заказа:", reply_markup=keyboard)
    else:
        await message.answer("Не удалось загрузить каталог цветов.")

# Обработка выбора цветка из инлайн-кнопок
@dp.callback_query(lambda c: c.data.startswith('flower_'))
async def handle_flower_selection(callback_query: CallbackQuery):
    username = callback_query.from_user.username
    flower_id = callback_query.data.split('_')[1]  # Предположим, что данные цветка передаются через callback
    user_id = await get_user_id_by_username(username)  # Получаем user_id по username

    if user_id:
        order_success = await place_order_via_bot(user_id=user_id, flower_id=flower_id)
        if order_success:
            await callback_query.message.answer("Заказ успешно оформлен!")
        else:
            await callback_query.message.answer("Произошла ошибка при оформлении заказа.")
    else:
        await callback_query.message.answer("Не удалось получить ID пользователя.")

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
