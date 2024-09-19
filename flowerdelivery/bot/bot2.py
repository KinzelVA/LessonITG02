# flowerdelivery\bot\bot2.py
import os
import sys
import django

# Определяем путь к корневой директории проекта
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Добавляем корневую директорию в sys.path
if project_root not in sys.path:
    sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowerdelivery.settings')  # Убедитесь, что 'flowerdelivery.settings' это путь к вашим настройкам Django
django.setup()  # Инициализация Django

import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton
from config import BOT_TOKEN
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
import aiohttp
from aiogram.filters import StateFilter  # Импортируем StateFilter для фильтрации по состояниям
import asyncio
from aiogram.fsm.context import FSMContext
from bot_func import register_user_via_bot, create_order_in_db, get_or_create_test_user, get_flower_catalog, get_user_orders, send_review_to_site
from asgiref.sync import sync_to_async  # Импортируем sync_to_async для использования асинхронных функций
from django.contrib.auth.models import User  # Импортируем модель User




# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Определение состояний
class RegisterStates(StatesGroup):
    awaiting_username = State()
    awaiting_password = State()
    awaiting_password_confirm = State()
    awaiting_email = State()

class CartStates(StatesGroup):
    awaiting_quantity = State()
    awaiting_address = State()
    awaiting_payment_method = State()
    confirming_order = State()

# Создание клавиатуры
def create_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Каталог цветов"), KeyboardButton(text="Отзывы"), KeyboardButton(text="Оформить заказ")],
            [KeyboardButton(text="Мои заказы"), KeyboardButton(text="Оплата"), KeyboardButton(text="Регистрация")]
        ],
        resize_keyboard=True
    )

# Команда /start
@dp.message(CommandStart())
async def start(message: Message):
    keyboard = create_keyboard()
    await message.answer("Добро пожаловать в FlowerDelivery! Вы можете делать заказы цветов через этот бот", reply_markup=keyboard)

# Обработка команды "Регистрация"
@dp.message(lambda message: message.text == "Регистрация")
async def handle_register_button(message: Message, state: FSMContext):
    await message.answer("Введите ваше имя пользователя:")
    await state.set_state(RegisterStates.awaiting_username)

@dp.message(RegisterStates.awaiting_username)
async def process_username(message: Message, state: FSMContext):
    username = message.text
    await state.update_data(username=username)
    await message.answer("Введите ваш пароль:")
    await state.set_state(RegisterStates.awaiting_password)

@dp.message(RegisterStates.awaiting_password)
async def process_password(message: Message, state: FSMContext):
    password = message.text
    await state.update_data(password=password)
    await message.answer("Введите ваш email:")
    await state.set_state(RegisterStates.awaiting_email)

@dp.message(RegisterStates.awaiting_email)
async def process_email(message: Message, state: FSMContext):
    email = message.text
    user_data = await state.get_data()
    username = user_data["username"]
    password = user_data["password"]

    # Регистрируем пользователя напрямую через базу данных
    registration_success = await register_user_via_bot(username, password, email)

    if registration_success is True:
        await message.answer("Регистрация прошла успешно!")
    else:
        await message.answer(f"Произошла ошибка: {registration_success}")
    await state.clear()

# Обработка команды "Оформить заказ"
@dp.message(lambda message: message.text == "Оформить заказ")
async def confirm_order(message: Message, state: FSMContext):
    user_data = await state.get_data()
    cart = user_data.get('cart', [])

    if not cart:
        await message.answer("Ваша корзина пуста.")
        return

    # Получаем пользователя по его имени в Telegram
    user = await get_or_create_test_user(message.from_user.username)

    # Создаем заказ в базе данных
    order = await create_order_in_db(user, cart)

    # Отправляем уведомление суперпользователю KinzelVA
    superuser = await sync_to_async(User.objects.get)(username="KinzelVA")
    await bot.send_message(superuser.id, f"Новый заказ №{order.id} от {user.username}")

    await message.answer("Ваш заказ был успешно оформлен!")
    await state.clear()

# Обработка команды "Каталог цветов"
@dp.message(lambda message: message.text == "Каталог цветов")
async def show_flower_catalog(message: Message):
    try:
        # Получаем каталог цветов асинхронно
        flowers = await get_flower_catalog()

        logging.info(f"Загружено {len(flowers)} цветов.")

        if flowers:
            for flower in flowers:
                name = flower.name
                price = flower.price
                description = flower.description or 'Описание отсутствует'
                image_url = flower.image.url if flower.image else None

                if image_url:
                    try:
                        await message.answer_photo(
                            photo=image_url,
                            caption=f"{name}\nЦена: {price} руб.\nОписание: {description}"
                        )
                    except Exception as e:
                        logging.error(f"Ошибка при отправке фото: {e}")
                        await message.answer(f"{name}\nЦена: {price} руб.\nОписание: {description}")
                else:
                    await message.answer(f"{name}\nЦена: {price} руб.\nОписание: {description}")
        else:
            await message.answer("Каталог цветов пуст или не удалось загрузить.")
    except Exception as e:
        logging.error(f"Ошибка при загрузке каталога цветов: {str(e)}")
        await message.answer("Не удалось загрузить каталог цветов.")


# Обработка количества
@dp.message(CartStates.awaiting_quantity)
async def process_quantity(message: Message, state: FSMContext):
    try:
        quantity = int(message.text)
        if quantity <= 0:
            raise ValueError()

        user_data = await state.get_data()
        flower = user_data['selected_flower']
        cart = user_data.get('cart', [])
        cart.append({'flower': flower, 'quantity': quantity})
        await state.update_data(cart=cart)

        await message.answer(
            f"Добавлено {quantity} шт. {flower['name']} в корзину. Напишите 'Оформить заказ' для завершения или 'Каталог', чтобы добавить еще.")
        await state.set_state(CartStates.confirming_order)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное количество.")

# Обработка команды "Отзывы"
@dp.message(lambda message: message.text == "Отзывы")
async def handle_review(message: Message, state: FSMContext):
    username = message.from_user.username or message.from_user.full_name

    # Получаем список заказов пользователя
    orders = await get_user_orders(username)

    if orders:
        flowers = []
        flower_ids = set()
        for order in orders:
            for flower in order['flowers']:
                if flower['id'] not in flower_ids:
                    flowers.append(flower)
                    flower_ids.add(flower['id'])

        flower_buttons = [
            InlineKeyboardButton(text=flower['name'], callback_data=f"review_flower_{flower['id']}") for flower in flowers
        ]
        flower_keyboard = InlineKeyboardMarkup(inline_keyboard=[flower_buttons])

        await message.answer("Выберите цветок, на который хотите оставить отзыв:", reply_markup=flower_keyboard)
        await state.set_state("awaiting_flower_selection_review")
    else:
        await message.answer("У вас нет заказов, на которые можно оставить отзыв.")

# Основная функция
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
