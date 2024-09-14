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


# Функция для получения заказов пользователя
async def get_user_orders(username):
    url = f"http://127.0.0.1:8000/api/orders/?username={username}"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()  # Возвращает список заказов
                else:
                    logging.error(f"Ошибка загрузки заказов. Код ответа: {response.status}")
                    return None
    except Exception as e:
        logging.error(f"Ошибка при запросе заказов: {str(e)}")
        return None

# Функция для отправки отзыва на сайт
async def send_review_to_site(username, flower_id, review_text, rating=None):
    # Получаем ID пользователя по имени
    user_id = 1

    if not user_id:
        logging.error("Не удалось получить ID пользователя. Отзыв не может быть отправлен.")
        return False

    url = "http://127.0.0.1:8000/api/reviews/"
    data = {
        'user': user_id,  # Передаём ID пользователя
        'flower': flower_id,
        'review': review_text,
        'rating': rating if rating is not None else 5  # По умолчанию 5, если рейтинг не указан
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status == 201:
                    return True
                else:
                    error_response = await response.text()
                    logging.error(f"Ошибка при отправке отзыва. Код ответа: {response.status}. Ответ: {error_response}")
                    return False
    except Exception as e:
        logging.error(f"Ошибка при запросе отзыва: {str(e)}")
        return False


# Функция для получения ID пользователя по имени
async def get_user_id_by_username(username):
    url = f"http://127.0.0.1:8000/api/users/?username={username}"
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