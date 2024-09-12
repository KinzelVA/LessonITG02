import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton
from config import BOT_TOKEN  # Убедитесь, что у вас есть токен бота
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State  # Для объявления состояний
import aiohttp
import asyncio
from aiogram.fsm.context import FSMContext
from bot_func import register_user_via_bot, get_flower_catalog, get_user_id_by_username, place_order_via_bot, get_flower_details

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
    awaiting_address = State()

class CartStates(StatesGroup):
    awaiting_quantity = State()
    awaiting_address = State()
    awaiting_payment_method = State()
    confirming_order = State()

# Создание клавиатуры
def create_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Каталог цветов"), KeyboardButton(text="Оформить заказ")],
            [KeyboardButton(text="Мои заказы"), KeyboardButton(text="Оплата"), KeyboardButton(text="Регистрация")]
        ],
        resize_keyboard=True
    )

# Команда /start
@dp.message(CommandStart())
async def start(message: Message):
    keyboard = create_keyboard()
    await message.answer("Добро пожаловать в FlowerDelivery!", reply_markup=keyboard)

# Обработка команды "Регистрация"
@dp.message(lambda message: message.text == "Регистрация")
async def handle_register_button(message: Message, state: FSMContext):
    await message.answer("Введите ваше имя пользователя:")
    await state.set_state(RegisterStates.awaiting_username)

# Обработка имени пользователя
@dp.message(RegisterStates.awaiting_username)
async def process_username(message: Message, state: FSMContext):
    username = message.text
    await state.update_data(username=username)
    await message.answer("Введите ваш пароль:")
    await state.set_state(RegisterStates.awaiting_password)

# Обработка пароля
@dp.message(RegisterStates.awaiting_password)
async def process_password(message: Message, state: FSMContext):
    password = message.text
    await state.update_data(password=password)
    await message.answer("Введите ваш email:")
    await state.set_state(RegisterStates.awaiting_email)

# Обработка email и завершение регистрации
@dp.message(RegisterStates.awaiting_email)
async def process_email(message: Message, state: FSMContext):
    email = message.text
    await state.update_data(email=email)
    await message.answer("Введите ваш адрес для доставки:")
    await state.set_state(RegisterStates.awaiting_address)

@dp.message(RegisterStates.awaiting_address)
async def process_address(message: Message, state: FSMContext):
    address = message.text
    user_data = await state.get_data()
    username = user_data["username"]
    password = user_data["password"]
    email = user_data["email"]
    registration_success = await register_user_via_bot(username, password, email, address)
    if registration_success:
        await message.answer("Регистрация прошла успешно!")
    else:
        await message.answer("Произошла ошибка при регистрации.")
    await state.clear()

# Обработка команды "Каталог цветов"
@dp.message(lambda message: message.text == "Каталог цветов")
async def show_flower_catalog(message: Message):
    flowers = await get_flower_catalog()
    if flowers:
        for flower in flowers:
            name = flower['name']
            price = flower['price']
            description = flower.get('description', 'Описание отсутствует')
            image_url = f"{flower.get('image')}"
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

        inline_keyboard = [[InlineKeyboardButton(text=f"{flower['name']} - {flower['price']} руб.", callback_data=f"flower_{flower['id']}")] for flower in flowers]
        keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        await message.answer("Выберите цветок для заказа:", reply_markup=keyboard)
    else:
        await message.answer("Не удалось загрузить каталог цветов.")

# Обработка выбора цветка
@dp.callback_query(lambda c: c.data.startswith('flower_'))
async def handle_flower_selection(callback_query: CallbackQuery, state: FSMContext):
    flower_id = callback_query.data.split('_')[1]
    flowers = await get_flower_catalog()
    flower = next((f for f in flowers if f['id'] == int(flower_id)), None)
    if flower:
        await state.update_data(selected_flower=flower)
        await callback_query.message.answer(f"Вы выбрали {flower['name']} за {flower['price']} руб. Сколько хотите добавить?")
        await state.set_state(CartStates.awaiting_quantity)
    else:
        await callback_query.message.answer("Ошибка! Цветок не найден.")

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
        cart.append({'flower': flower, 'quantity': quantity, 'total': quantity * float(flower['price'])})
        await state.update_data(cart=cart)
        await message.answer(f"Добавлено {quantity} шт. {flower['name']} в корзину. Напишите 'Оформить заказ' или 'Вернуться в каталог'.")
        await state.set_state(CartStates.confirming_order)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное количество.")

# Подтверждение заказа
@dp.message(CartStates.confirming_order)
async def confirm_order(message: Message, state: FSMContext):
    if message.text.lower() == "оформить заказ":
        user_data = await state.get_data()
        cart = user_data.get('cart', [])
        if not cart:
            await message.answer("Ваша корзина пуста.")
            return
        total_sum = sum(item['total'] for item in cart)
        cart_items = "\n".join([f"{item['flower']['name']} - {item['quantity']} шт. на {item['total']} руб." for item in cart])
        await message.answer(f"Ваш заказ:\n{cart_items}\n\nОбщая сумма: {total_sum} руб.")
        await message.answer("Пожалуйста, укажите адрес доставки:")
        await state.set_state(CartStates.awaiting_address)
    elif message.text.lower() == "вернуться в каталог":
        await start(message)
    else:
        await message.answer("Введите 'Оформить заказ' или 'Вернуться в каталог'.")

# Обработка адреса
@dp.message(CartStates.awaiting_address)
async def process_address(message: Message, state: FSMContext):
    address = message.text
    await state.update_data(address=address)
    await message.answer("Адрес сохранен. Теперь перейдите к оплате, используя команду 'Оплата'.")
    await state.set_state(CartStates.awaiting_payment_method)

@dp.message(lambda message: message.text == "Мои заказы")
async def my_orders(message: Message):
    username = message.from_user.username or message.from_user.full_name
    url = f"http://127.0.0.1:8000/api/orders/?username={username}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                orders = await response.json()

                if orders:
                    order_list = []
                    for order in orders:
                        order_id = order['id']
                        status = order['status']
                        flower_ids = order['flowers']

                        flower_names = []
                        for flower_id in flower_ids:
                            flower_data = await get_flower_details(flower_id)
                            if flower_data:
                                flower_names.append(flower_data['name'])

                        # Формируем строку для каждого заказа
                        order_list.append(f"Заказ №{order_id}: {', '.join(flower_names)} - {status}")

                    await message.answer(f"Ваши заказы:\n" + "\n".join(order_list))
                else:
                    await message.answer("У вас нет заказов.")
            else:
                await message.answer("Не удалось загрузить ваши заказы.")


# Обработка команды "Оплата"
@dp.message(lambda message: message.text == "Оплата")
async def handle_payment(message: Message, state: FSMContext):
    user_data = await state.get_data()
    address = user_data.get("address", None)
    cart = user_data.get("cart", [])
    if not cart:
        await message.answer("У вас нет оформленного заказа. Сначала оформите заказ.")
        return
    if not address:
        await message.answer("Сначала нужно ввести адрес доставки.")
        return
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Банковской картой", callback_data="pay_card")],
        [InlineKeyboardButton(text="Наличными курьеру", callback_data="pay_cash")]
    ])
    await message.answer("Выберите способ оплаты:", reply_markup=keyboard)
    await state.set_state(CartStates.awaiting_payment_method)

# Обработка способа оплаты
@dp.callback_query(lambda c: c.data.startswith('pay_'))
async def handle_payment_method(callback_query: CallbackQuery, state: FSMContext):
    if callback_query.data == "pay_card":
        await callback_query.message.answer("Оплата банковской картой прошла успешно!")
    elif callback_query.data == "pay_cash":
        await callback_query.message.answer("Оплата наличными курьеру пройдет при доставке!")
    user_data = await state.get_data()
    address = user_data.get("address", "адрес не указан")
    await callback_query.message.answer(f"Ваш заказ будет доставлен по адресу: {address} в течение часа.")
    await state.clear()

# Основная функция
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
