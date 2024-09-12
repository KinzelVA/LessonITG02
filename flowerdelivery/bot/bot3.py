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
