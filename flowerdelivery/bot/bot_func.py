import os
import sys
import django

# Определяем путь к корневой директории проекта (где находится manage.py)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Добавляем корневую директорию в sys.path
if project_root not in sys.path:
    sys.path.append(project_root)
# Устанавливаем переменную окружения для Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowerdelivery.settings')

# Инициализируем Django
django.setup()
import aiohttp
import logging
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async


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

async def get_or_create_test_user():
    # Функция для создания или получения фиктивного пользователя
    user, created = User.objects.get_or_create(username='test_user', defaults={'password': 'test'})
    return user
# Функция для отправки отзыва на сайт
async def send_review_to_site(username, flower_id, review_text, rating=None):
    test_user = await get_or_create_test_user()
    url = "http://127.0.0.1:8000/api/reviews/"
    data = {
        'user': test_user.id,  # Передаём ID пользователя
        'flower': flower_id,
        'review': review_text,
        'rating': rating if rating is not None else 5  # По умолчанию 5, если рейтинг не указан
    }

    try:
        async with aiohttp.ClientSession(headers={'Content-Type': 'application/json'}) as session:
            async with session.post(url, json=data) as response:
                if response.status == 201:
                    return True
                elif response.status == 200:  # Код 200 тоже может быть успешным ответом
                    # Проверяем, что вернулся правильный ответ
                    response_text = await response.text()
                    if "Прекрасный цветок" in response_text:
                        return True
                    else:
                        logging.error(f"Ошибка при отправке отзыва. Ответ: {response_text}")
                        return False
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

# Функция для получения или создания тестового пользователя
async def get_or_create_test_user():
    # Используем sync_to_async для выполнения синхронной операции с базой данных в асинхронном контексте
    user, created = await sync_to_async(User.objects.get_or_create)(username='test_user', defaults={'password': 'test'})
    return user