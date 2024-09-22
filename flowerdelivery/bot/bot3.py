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

# Сохранение данных из ot2.py

@dp.message(lambda message: message.text == "Оформить заказ")
async def confirm_order(message: Message, state: FSMContext):
    user_data = await state.get_data()
    cart = user_data.get('cart', [])

    if not cart:
        await message.answer("Ваша корзина пуста.")
        return

    # Получаем пользователя по его имени в Telegram
    user = await get_or_create_test_user()

    # Создаем заказ в базе данных
    order = await create_order_in_db(user, cart)

    if order:

        superuser = await sync_to_async(User.objects.get)(username="KinzelVA")
        await bot.send_message(superuser.id, f"Новый заказ №{order.id} от {user.username}")

    await message.answer("Ваш заказ был успешно оформлен!")
    await state.clear()

# Обработка команды "Оплата"
@dp.message(lambda message: message.text == "Оплата")
async def handle_payment(message: Message, state: FSMContext):
    await message.answer("Введите адрес доставки:")
    await state.set_state(CartStates.awaiting_address)

@dp.message(CartStates.awaiting_address)
async def process_address(message: Message, state: FSMContext):
    address = message.text
    await state.update_data(address=address)
    await message.answer("Выберите способ оплаты:")
    await state.set_state(CartStates.awaiting_payment_method)

@dp.message(CartStates.awaiting_payment_method)
async def process_payment_method(message: Message, state: FSMContext):
    payment_method = message.text
    await state.update_data(payment_method=payment_method)

    user_data = await state.get_data()
    address = user_data["address"]

    await message.answer(f"Оплата прошла успешно!\nАдрес доставки: {address}\nМетод оплаты: {payment_method}")
    await state.clear()
