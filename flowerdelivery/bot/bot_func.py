import aiohttp
import logging

# Функция для регистрации пользователя через API
async def register_user_via_bot(username, password, email, address):
    url = "http://127.0.0.1:8000/api/register/"
    data = {'username': username, 'password': password, 'email': email, 'address': address}

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
                if response.status == 200:
                    return await response.json()  # Возвращает список цветов
                else:
                    logging.error(f"Ошибка загрузки каталога. Код ответа: {response.status}")
                    return None
    except Exception as e:
        logging.error(f"Ошибка при запросе каталога: {str(e)}")
        return None

# Функция для получения ID пользователя по имени
async def get_user_id_by_username(username):
    url = f"http://127.0.0.1:8000/api/api/users/?username={username}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    user_data = await response.json()
                    logging.info(f"Получен ответ от API: {user_data}")
                    if user_data and 'id' in user_data:
                        return user_data['id']
                    else:
                        logging.error(f"Пользователь с именем {username} не найден")
                        return None
                else:
                    logging.error(f"Ошибка при получении ID пользователя. Код ответа: {response.status}")
                    return None
    except Exception as e:
        logging.error(f"Ошибка при запросе ID пользователя: {str(e)}")
        return None

# Функция для оформления заказа через API
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
                    logging.error(f"Ошибка при оформлении заказа. Код ответа: {response.status}, Ответ: {error_json}")
                    return False
    except Exception as e:
        logging.error(f"Ошибка при оформлении заказа: {str(e)}")
        return False

async def get_flower_details(flower_id):
    url = f"http://127.0.0.1:8000/shop/api/flowers/{flower_id}/"  # Предположим, это правильный URL
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()  # Возвращает данные о цветке
                else:
                    logging.error(f"Не удалось загрузить данные о цветке {flower_id}. Код ответа: {response.status}")
                    return None
    except Exception as e:
        logging.error(f"Ошибка при запросе данных о цветке: {str(e)}")
        return None