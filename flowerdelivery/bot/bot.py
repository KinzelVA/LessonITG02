import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from config import  API_URL  # Убедитесь, что у вас есть токен бота
import requests
import asyncio
import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

BASE_URL = API_URL  # Замените на ваш API URL
REGISTER_URL = BASE_URL + 'users/api/register/'  # URL для регистрации пользователя
FLOWERS_URL = BASE_URL + 'shop/api/flowers/'  # URL для получения каталога товаров
CREATE_ORDER_URL = BASE_URL + 'api/orders/'  # URL для создания заказа


# Функция для регистрации пользователя
def register_user(username, email, password):
    data = {
        'username': username,
        'email': email,
        'password1': password,
        'password2': password
    }

    response = requests.post(REGISTER_URL, data=data)
    if response.status_code == 201:
        return 'Пользователь успешно зарегистрирован!'
    else:
        return f'Ошибка регистрации: {response.json()}'


# Функция для получения списка цветов
def get_catalog():
    response = requests.get(FLOWERS_URL)
    if response.status_code == 200:
        flowers = response.json()
        catalog = "Каталог цветов:\n"
        for flower in flowers:
            catalog += f"{flower['name']} - {flower['price']} руб. - {flower['description']}\n"
        return catalog
    else:
        return f'Ошибка получения каталога: {response.status_code}'


# Функция для создания заказа
def create_order(user_token, flower_id):
    headers = {
        'Authorization': f'Token {user_token}'  # Передача токена для аутентификации
    }
    data = {
        'flower_id': flower_id
    }
    response = requests.post(CREATE_ORDER_URL, headers=headers, data=data)
    if response.status_code == 201:
        return 'Заказ успешно оформлен!'
    else:
        return f'Ошибка оформления заказа: {response.json()}'


# Команда для старта
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Добро пожаловать в FlowerDelivery! Вы можете зарегистрироваться, сделать заказ или просмотреть каталог.")


# Команда для регистрации
@dp.message(Command('register'))
async def register(message: Message):
    await message.answer("Введите ваши данные в формате: Имя Пользователя, Email, Пароль")


# Обработка данных регистрации
@dp.message(lambda message: ',' in message.text)
async def handle_registration(message: Message):
    user_data = message.text.split(',')
    if len(user_data) == 3:
        username, email, password = [x.strip() for x in user_data]
        result = register_user(username, email, password)
        await message.answer(result)
    else:
        await message.answer("Пожалуйста, введите данные в правильном формате: Имя Пользователя, Email, Пароль")


# Команда для получения каталога
@dp.message(Command('catalog'))
async def show_catalog(message: Message):
    catalog = get_catalog()
    await message.answer(catalog)


# Команда для оформления заказа
@dp.message(Command('new_order'))
async def new_order(message: Message):
    await message.answer("Введите ID цветка для оформления заказа.")


# Обработка ID заказа
@dp.message(lambda message: message.text.isdigit())
async def handle_order_id(message: Message):
    flower_id = message.text
    user_token = 'your_user_token_here'  # Здесь должен быть токен пользователя
    result = create_order(user_token, flower_id)
    await message.answer(result)


# Функция для получения списка заказов через API
async def get_orders():
    async with aiohttp.ClientSession() as session:
        async with session.get(BASE_URL + "api/orders/") as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                return None


# Функция для уведомления о новом заказе
async def notify_new_order(order_data):
    message = f"Новый заказ №{order_data['id']} от {order_data['user']}"
    await bot.send_message(chat_id='CHAT_ID', text=message)


# Создание меню для пользователя
def get_main_menu():
    buttons = [
        [KeyboardButton(text="📋 Каталог"), KeyboardButton(text="🛒 Оформить заказ")],
        [KeyboardButton(text="🔑 Зарегистрироваться"), KeyboardButton(text="🚪 Войти")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# Команда /start, которая приветствует пользователя и отображает меню
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Добро пожаловать в FlowerDelivery! Выберите команду из меню.", reply_markup=get_main_menu())

# Обработчик команды "Зарегистрироваться"
@dp.message(Command('Зарегистрироваться'))
async def register_user(message: Message):
    await message.answer("Для регистрации введите ваш email и пароль в формате: email пароль")

@dp.message(lambda message: len(message.text.split()) == 2)
async def handle_registration(message: Message):
    email, password = message.text.split()
    response = requests.post(f"{API_URL}/register/", data={'email': email, 'password': password})
    if response.status_code == 201:
        await message.answer("Вы успешно зарегистрированы!", reply_markup=get_main_menu())
    else:
        await message.answer("Ошибка при регистрации. Попробуйте снова.")

# Команда для получения каталога
@dp.message(Command('Каталог'))
async def catalog(message: Message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/catalog/") as response:
            if response.status == 200:
                catalog_data = await response.json()
                catalog_items = "\n".join([f"{item['name']} - {item['price']} руб." for item in catalog_data])
                await message.answer(f"Каталог:\n{catalog_items}")
            else:
                await message.answer("Не удалось загрузить каталог.")

# Команда "Оформить заказ"
@dp.message(Command('Оформить заказ'))
async def new_order(message: Message):
    await message.answer("Введите ID цветка из каталога для оформления заказа.")

@dp.message(lambda message: message.text.isdigit())
async def handle_order(message: Message):
    flower_id = message.text
    headers = {
        'Authorization': f'Token {user_token}',  # Здесь подставьте токен, который вы получите при регистрации/входе
    }
    response = requests.post(f"{API_URL}/orders/", headers=headers, data={'flower_id': flower_id})
    if response.status_code == 201:
        await message.answer("Заказ успешно оформлен!")
    else:
        await message.answer("Ошибка при оформлении заказа. Попробуйте снова.")
# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())



