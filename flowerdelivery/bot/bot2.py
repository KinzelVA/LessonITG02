#bot2.py
import os
import sys
import django
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram import F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.filters import StateFilter
from asgiref.sync import sync_to_async
from config import BOT_TOKEN
import asyncio

# Определение пути к корневой директории проекта
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Добавление корневой директории в sys.path
if project_root not in sys.path:
    sys.path.append(project_root)

# Установка переменной окружения для настройки Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowerdelivery.settings')

# Инициализация Django
django.setup()

# Импорт после настройки окружения Django
from shop.models import Flower
from flower_orders.models import OrderItem, Order
from bot_func import (
    register_user_via_bot,
    create_order_in_db,
    get_flower_catalog,
    get_user_orders,
    send_review_to_site
)
from django.contrib.auth.models import User

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
# Обработка команды "Каталог цветов"
@dp.message(lambda message: message.text == "Каталог цветов")
async def show_flower_catalog(message: Message):
    try:
        # Получаем каталог цветов
        flowers = await get_flower_catalog()

        if not flowers:
            await message.answer("Каталог цветов пуст или не удалось загрузить данные.")
            return

        # Выводим информацию о цветах
        for flower in flowers:
            name = flower.name
            price = flower.price
            description = flower.description or 'Описание отсутствует'

            # Новый код для отправки изображения из файла
        image_path = f"media/{flower.image}"  # Относительный путь к изображению

        # Пытаемся открыть файл и отправить его
        try:
            with open(image_path, 'rb') as image_file:
                await message.answer_photo(photo=image_file,
                                           caption=f"{flower.name}\nЦена: {flower.price} руб.\nОписание: {flower.description}")
        except FileNotFoundError:
            await message.answer(f"Изображение для {flower.name} не найдено.")

        # Добавляем кнопки для выбора цветов с ценами
        buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"{flower.name} - {flower.price} руб.", callback_data=f"select_flower_{flower.id}")] for flower in flowers
            ]
        )

        # Отправляем кнопки под списком цветов
        await message.answer("Выберите цветок для заказа:", reply_markup=buttons)

    except Exception as e:
        logging.error(f"Ошибка при загрузке каталога: {str(e)}")
        await message.answer(f"Произошла ошибка при загрузке каталога цветов: {str(e)}")

# Обработка нажатия на кнопку "Выбрать"
@dp.callback_query(lambda c: c.data.startswith('select_flower_'))
async def select_flower(callback_query: types.CallbackQuery, state: FSMContext):
    flower_id = int(callback_query.data.split('_')[-1])
    # Сохраняем выбранный цветок в состоянии
    flower = await sync_to_async(Flower.objects.get)(id=flower_id)
    await state.update_data(selected_flower={'id': flower.id, 'name': flower.name})

    await bot.send_message(callback_query.from_user.id, f"Сколько штук {flower.name} вы хотите заказать?")
    await state.set_state(CartStates.awaiting_quantity)

# Обработка команды "Отзывы"
@dp.message(lambda message: message.text == "Отзывы")
async def handle_review(message: Message, state: FSMContext):
    username = message.from_user.username or message.from_user.full_name

    # Получаем список заказов пользователя
    orders = await sync_to_async (get_user_orders)(username)

    if orders:
        flowers = []
        flower_ids = set()
        for order in orders:
            for flower in order.flowers.all():
                if flower.id not in flower_ids:
                    flowers.append(flower)
                    flower_ids.add(flower.id)

        flower_buttons = [
            InlineKeyboardButton(text=flower.name, callback_data=f"review_flower_{flower.id}") for flower in flowers
        ]
        flower_keyboard = InlineKeyboardMarkup(inline_keyboard=[flower_buttons])

        await message.answer("Выберите цветок, на который хотите оставить отзыв:", reply_markup=flower_keyboard)
        await state.set_state("awaiting_flower_selection_review")
    else:
        await message.answer("У вас нет заказов, на которые можно оставить отзыв.")

    # Обработка выбора цветка для отзыва


@dp.callback_query(lambda callback_query: callback_query.data.startswith("review_flower_"))
async def handle_flower_selection(callback_query: CallbackQuery, state: FSMContext):
    flower_id = int(callback_query.data.split("_")[-1])
    await state.update_data(flower_id=flower_id)
    await callback_query.message.answer("Напишите ваш отзыв о выбранном цветке:")
    await state.set_state("awaiting_review_text")


# Обработка текста отзыва
@dp.message(StateFilter("awaiting_review_text"))
async def handle_review_text(message: Message, state: FSMContext):
    review_text = message.text
    user_data = await state.get_data()
    flower_id = user_data["flower_id"]
    username = message.from_user.username or message.from_user.full_name

    # Отправляем отзыв на сайт через функцию send_review_to_site
    success = await send_review_to_site(username, flower_id, review_text)

    if success:
        await message.answer("Спасибо за ваш отзыв!")
    else:
        await message.answer("Произошла ошибка при отправке отзыва. Попробуйте позже.")

    await state.clear()

# Обработка команды "Оформить заказ"
@dp.message(lambda message: message.text == "Оформить заказ")
async def confirm_order(message: Message, state: FSMContext):
    user_data = await state.get_data()
    cart = user_data.get('cart', [])

    if not cart:
        await message.answer("Ваша корзина пуста.")
        return

    username = message.from_user.username
    telegram_user_id = message.from_user.id

    # Получаем или создаем пользователя
    user, created = await sync_to_async(User.objects.get_or_create)(
        username=username,
        defaults={"telegram_user_id": telegram_user_id}
    )

    if created:
        print(f"Создан новый пользователь: {username}.")
    else:
        print(f"Найден существующий пользователь: {username}.")

    # Создаем заказ в базе данных
    order = await create_order_in_db(user, cart)

    if order:
        order_details = ""
        total_price = 0

        # Формируем детали заказа
        for item in cart:
            flower_data = item.get('flower')
            flower_id = flower_data.get('id')
            flower = await sync_to_async(Flower.objects.get)(id=flower_id)  # Теперь асинхронно
            quantity = item.get('quantity', 0)

            # Проверка наличия ключа 'price'
            price_per_item = flower.price
            if price_per_item is None:
                await message.answer(f"Произошла ошибка: для цветка {flower.name} не указана цена.")
                continue

            item_total = quantity * price_per_item
            total_price += item_total
            order_details += f"{flower.name} - {quantity} шт. по {price_per_item} руб. = {item_total} руб.\n"

        order_summary = f"Ваш заказ успешно оформлен!\nДетали заказа:\n{order_details}Общая сумма: {total_price} руб. теперь вы можете перейти к оплате, нажав кнопку оплата в нижнем меню."
        await message.answer(order_summary)
        await state.clear()
    else:
        await message.answer("Произошла ошибка при оформлении заказа.")

@dp.message(F.text == "/get_my_id")
async def get_my_id(message: Message):
    await message.answer(f"Твой chat_id: {message.chat.id}")


# Обработка команды "Оплата"
@dp.message(lambda message: message.text == "Оплата")
async def handle_payment(message: Message, state: FSMContext):
    await message.answer("Введите адрес доставки:")
    await state.set_state(CartStates.awaiting_address)


# Обработка адреса доставки
@dp.message(CartStates.awaiting_address)
async def process_address(message: Message, state: FSMContext):
    address = message.text
    await state.update_data(address=address)

    # Формируем кнопки для выбора метода оплаты
    payment_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Банковской картой", callback_data="payment_card")],
            [InlineKeyboardButton(text="Наличными курьеру", callback_data="payment_cash")]
        ]
    )

    # Отправляем сообщение с кнопками выбора оплаты
    await message.answer("Выберите способ оплаты:", reply_markup=payment_buttons)
    await state.set_state(CartStates.awaiting_payment_method)


# Обработка способа оплаты
@dp.callback_query(lambda c: c.data.startswith("payment_"))
async def process_payment_method(callback_query: types.CallbackQuery, state: FSMContext):
    payment_method = callback_query.data.split("_")[-1]

    # Определяем метод оплаты в зависимости от нажатой кнопки
    if payment_method == "card":
        payment_method_text = "Банковской картой"
    elif payment_method == "cash":
        payment_method_text = "Наличными курьеру"

    await state.update_data(payment_method=payment_method_text)

    # Получаем данные пользователя, корзины и адреса
    user_data = await state.get_data()
    address = user_data["address"]

    await bot.send_message(callback_query.from_user.id,
                           f"Оплата прошла успешно! Спасибо за покупку! Ваш заказ будет доставлен в течение 1 часа.\nАдрес доставки: {address}\nМетод оплаты: {payment_method_text}")
    await state.clear()

# Команда "Мои заказы"
@dp.message(lambda message: message.text == "Мои заказы")
async def show_orders(message: Message):
    try:
        username = message.from_user.username or message.from_user.full_name

        if not username:
            await message.answer("Не удалось определить имя пользователя. Попробуйте позже.")
            return

        # Используем sync_to_async для асинхронного взаимодействия с базой данных
        orders = await get_user_orders(username)

        if orders:
            order_text = ""
            for order in orders:
                order_text += f"Заказ №{order.id} - Статус: {order.status}\n"

                # Асинхронный доступ к элементам заказа
                order_items = await sync_to_async(list)(order.items.all())

                # Логирование цветов для каждого заказа
                for item in order_items:
                    order_text += f"Цветок: {item.flower.name}, Количество: {item.quantity}\n"

            await message.answer(f"Ваши заказы:\n{order_text}")
        else:
            await message.answer("У вас нет заказов.")
    except Exception as e:
        await message.answer(f"Произошла ошибка при загрузке заказов: {str(e)}")


# Обработка количества
@dp.message(CartStates.awaiting_quantity)
async def process_quantity(message: Message, state: FSMContext):
    try:
        quantity = int(message.text)
        if quantity <= 0:
            raise ValueError()

        user_data = await state.get_data()
        selected_flower = user_data['selected_flower']
        cart = user_data.get('cart', [])
        cart.append({'flower': selected_flower, 'quantity': quantity})
        await state.update_data(cart=cart)

        await message.answer(
            f"Добавлено {quantity} шт. {selected_flower['name']} в корзину. Нажмите кнопку в нижнем меню 'Оформить заказ' для завершения или 'Каталог', чтобы добавить еще.")
        await state.set_state(CartStates.confirming_order)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное количество.")

# Основная функция
async def main():
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())
