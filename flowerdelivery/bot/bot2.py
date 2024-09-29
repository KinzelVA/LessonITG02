#bot2.py
import os
import sys
import django
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.filters import Command
from aiogram import F
from aiogram.types import FSInputFile
from aiogram.types import InputFile
from django.conf import settings
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
from flower_orders.models import Order
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

@dp.message(Command('help'))
async def help(message: Message):
    await message.answer("Я помогу вам оформить заказ. Зайдите в нижнее меню, нажав квадратик с четырьмя точками"
                         "он расположен справа в строке ввода сообщений, нажмите кнопку Регистрация,"
                         "ответьте на вопросы и бот вас зарегисстрирует. Затем в меню нажмите кнопку Каталог цветов, просмотрите"
                         " каталог, выберите цветы укажете количество в строке сообщений и отправите боту. Количество для каждого цветка надо отправлять"
                         "каждый раз. Затем нажимаете кнопку Оформить заказ и увидев ваш заказ в деталях: количество цветов, цена, общая сумма"
                         "заказа, переходите к оплате, нажав кнопку Оплата, введите адрес доставки, выберите способоплаты оплатите и получите"
                         "сообщение о том, что ваш заказ будет доставлен вам по адресу введенному вами и в какое время"
                         "Все ваш заказ принят. Счастливых покупок! В меню так же есть кнопка Мои заказы, где вы можете посмотреть ваш заказ,"
                         " а так же кнопка Отзывы, где вы можете оставить отзыв о качестве цветов и окачестве обслуживания.")



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
async def show_flower_catalog(message: types.Message):
    flowers = await get_flower_catalog()  # Используем await для асинхронного вызова
    if flowers:
        keyboard_buttons = []  # Список для кнопок

        for flower in flowers:
            print(f"Цветок: {flower}")  # Логируем данные о цветке

            flower_id = flower['id']  # Получаем реальный id из данных о цветке

            # Отображение изображения
            image_path = flower['image_url']  # Получаем путь к изображению
            if image_path and os.path.exists(image_path):  # Проверяем, что файл существует
                image_file = FSInputFile(image_path)
                await message.answer_photo(
                    photo=image_file,
                    caption=f"{flower['name']}\nЦена: {flower['price']} руб.\n{flower['description']}"
                )
            else:
                await message.answer(
                    f"Изображение для {flower['name']} не найдено. Проверьте путь: {image_path}"
                )

            # Создание кнопки для каждого цветка
            button = InlineKeyboardButton(text=flower['name'], callback_data=f"select_flower_{flower_id}")
            keyboard_buttons.append([button])  # Добавляем кнопку в список

        # Создаем клавиатуру и передаем список кнопок
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

        # Отправляем сообщение с клавиатурой
        await message.answer("Выберите цветок для заказа:", reply_markup=keyboard)
    else:
        await message.answer("Каталог цветов пуст или не удалось загрузить данные.")


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
    orders = await get_user_orders(username)

    if orders:
        flowers = []
        flower_ids = set()
        for order in orders:
            # Проверяем, что order.order_details не пустой
            if order.order_details:
                flower_lines = order.order_details.split("\n")
                for line in flower_lines:
                    if line.strip():  # Если строка не пустая
                        try:
                            flower_name = line.split(" - ")[0].strip()  # Извлекаем имя цветка
                            flower = await sync_to_async(Flower.objects.get)(name=flower_name)  # Ищем объект Flower
                            if flower.id not in flower_ids:  # Убеждаемся, что этого цветка еще нет в списке
                                flowers.append(flower)
                                flower_ids.add(flower.id)
                        except Flower.DoesNotExist:
                            print(f"Цветок с именем {flower_name} не найден.")
                            continue
            #else:
                #await message.answer(f"У заказа №{order.id} нет деталей.")

        # Если найдены цветы, создаем кнопки для выбора
        if flowers:
            flower_buttons = [
                InlineKeyboardButton(text=flower.name, callback_data=f"review_flower_{flower.id}") for flower in flowers
            ]
            flower_keyboard = InlineKeyboardMarkup(inline_keyboard=[flower_buttons])
            await message.answer("Выберите цветок, на который хотите оставить отзыв:", reply_markup=flower_keyboard)
            await state.set_state("awaiting_flower_selection_review")
        else:
            await message.answer("Не найдено цветков для отзывов.")
    else:
        await message.answer("У вас нет заказов, на которые можно оставить отзыв.")

# Обработка выбора цветка для отзыва
@dp.callback_query(lambda callback_query: callback_query.data.startswith("review_flower_"))
async def handle_flower_selection(callback_query: CallbackQuery, state: FSMContext):
    flower_id = int(callback_query.data.split("_")[-1])  # Получаем ID цветка из callback_data
    await state.update_data(flower_id=flower_id)
    flower = await sync_to_async(Flower.objects.get)(id=flower_id)  # Получаем объект цветка
    await callback_query.message.answer(f"Напишите ваш отзыв о выбранном цветке: {flower.name}")
    await state.set_state("awaiting_review_text")



# Обработка текста отзыва
@dp.message(StateFilter("awaiting_review_text"))
async def handle_review_text(message: Message, state: FSMContext):
    review_text = message.text
    user_data = await state.get_data()
    flower_id = user_data["flower_id"]  # Получаем ID цветка
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
    user, created = await sync_to_async (User.objects.get_or_create)(
        username=username,
        defaults={"telegram_user_id": telegram_user_id}
    )

    if created:
        print(f"Создан новый пользователь: {username}.")
    else:
        print(f"Найден существующий пользователь: {username}.")

    # Создаем заказ в базе данных
    try:
        order = await create_order_in_db(user, cart)

        if order:
            order_details = order.order_details
            total_price = order.total_price
            order_summary = f"Ваш заказ успешно оформлен!\nДетали заказа:\n{order_details}Общая сумма: {total_price} руб. Теперь вы можете перейти к оплате."
            await message.answer(order_summary)
        else:
            await message.answer("Произошла ошибка при оформлении заказа.")
    except Exception as e:
        print(f"Ошибка при оформлении заказа: {str(e)}")
        await message.answer(f"Произошла ошибка при оформлении заказа: {str(e)}")

    # После успешного создания заказа, отправляем уведомление суперпользователю
    superuser_chat_id = 5141125304  # Ваш chat_id

    order_summary = f"Поступил новый заказ от {user.username}.\nОбщая сумма заказа: {order.total_price} руб.\nДетали заказа:\n{order.order_details}"

    # Отправляем сообщение суперпользователю
    await bot.send_message(chat_id=superuser_chat_id, text=order_summary)

    await state.clear()


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

        # Получаем заказы пользователя
        orders = await get_user_orders(username)

        # Ограничиваем вывод 8 последними заказами
        displayed_orders = orders[-8:]

        if displayed_orders:
            order_text = ""
            for order in displayed_orders:
                # Форматируем дату без миллисекунд
                order_date = order.created_at.strftime('%Y-%m-%d %H:%M')

                # Добавляем основные данные о заказе
                order_text += (
                    f"Заказ №{order.id} - Статус: {order.status}\n"
                    f"Дата заказа: {order_date}\n"
                    f"Общая сумма: {order.total_price} руб.\n"
                    f"Детали заказа:\n{order.order_details}\n"
                )

                # Разделитель для разных заказов
                order_text += "------------------------\n"

            # Отправляем текст с заказами
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
        selected_flower = user_data.get('selected_flower')

        if not selected_flower:
            await message.answer("Произошла ошибка: не удалось найти выбранный цветок.")
            return

        # Получаем объект цветка из базы данных по его ID
        flower = await sync_to_async(Flower.objects.get)(id=selected_flower['id'])

        if not flower:
            await message.answer("Произошла ошибка: не удалось найти цветок в базе данных.")
            return

        cart = user_data.get('cart', [])
        # Добавляем объект цветка в корзину
        cart.append({'flower': flower, 'quantity': quantity})

        await state.update_data(cart=cart)

        await message.answer(
            f"Добавлено {quantity} шт. {flower.name} в корзину. Нажмите кнопку в нижнем меню 'Оформить заказ' для завершения или 'Каталог', чтобы добавить еще.")
        await state.set_state(CartStates.confirming_order)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное количество.")

# Основная функция
async def main():
    await dp.start_polling(bot)
if __name__ == "__main__":
    asyncio.run(main())
