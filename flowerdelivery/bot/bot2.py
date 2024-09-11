import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton
from config import BOT_TOKEN  # Убедитесь, что у вас есть токен бота
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State  # Для объявления состояний
import aiohttp
import asyncio

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)

# Инициализация хранилища состояний
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Определение состояний для процесса регистрации
class RegisterStates(StatesGroup):
    awaiting_username = State()
    awaiting_password = State()
    awaiting_email = State()

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
async def register_user_via_bot(username, password, email):
    url = "http://127.0.0.1:8000/api/register/"
    data = {'username': username, 'password': password, 'email': email}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status == 201:
                    return True
                elif response.status == 400:  # Ошибка при регистрации
                    error_json = await response.json()
                    logging.error(f"Ошибка при регистрации. Код ответа: {response.status}, Ответ: {error_json}")
                    if 'username' in error_json:
                        return f"Пользователь с именем {username} уже существует."
                    else:
                        return "Ошибка регистрации: " + str(error_json)
                else:
                    error_text = await response.text()
                    logging.error(f"Ошибка при регистрации. Код ответа: {response.status}, Ответ: {error_text}")
                    return False
    except Exception as e:
        logging.error(f"Ошибка при запросе регистрации: {str(e)}")
        return False

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
                    user_data = await response.json()
                    logging.info(f"Получен ответ от API: {user_data}")  # Логируем ответ
                    if user_data and 'id' in user_data:
                        return user_data['id']  # Проверяем, что данные пользователя есть
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
async def handle_register_button(message: Message, state: FSMContext):
    await message.answer("Введите ваше имя пользователя:")
    await state.set_state(RegisterStates.awaiting_username)  # Устанавливаем состояние для регистрации

# Обработка введенного имени пользователя
@dp.message(RegisterStates.awaiting_username)
async def process_username(message: Message, state: FSMContext):
    username = message.text
    await state.update_data(username=username)
    await message.answer("Введите ваш пароль:")
    await state.set_state(RegisterStates.awaiting_password)

# Обработка введенного пароля
@dp.message(RegisterStates.awaiting_password)
async def process_password(message: Message, state: FSMContext):
    password = message.text
    await state.update_data(password=password)
    await message.answer("Введите ваш email:")
    await state.set_state(RegisterStates.awaiting_email)

# Обработка введенного email и завершение регистрации
@dp.message(RegisterStates.awaiting_email)
async def process_email(message: Message, state: FSMContext):
    email = message.text
    user_data = await state.get_data()

    username = user_data["username"]
    password = user_data["password"]

    # Вызов функции регистрации пользователя через API
    registration_success = await register_user_via_bot(username, password, email)

    if registration_success:
        await message.answer("Регистрация прошла успешно!")
    else:
        await message.answer("Произошла ошибка при регистрации.")

    # Сброс состояния
    await state.clear()

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
