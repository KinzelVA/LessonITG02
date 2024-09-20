# flowerdelivery\bot\bot_func.py
import os
import django
import sys
import logging
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from flower_orders.models import Flower, Order, OrderItem  # Импорт моделей из вашего приложения
from reviews.models import Review
# Определяем путь к корневой директории проекта (где находится manage.py)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Добавляем корневую директорию в sys.path, если она там отсутствует
if project_root not in sys.path:
    sys.path.append(project_root)

# Устанавливаем переменную окружения для Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowerdelivery.settings')

# Инициализация Django
django.setup()

@sync_to_async
def get_or_create_test_user():
    user, created = User.objects.get_or_create(username='test_user', defaults={'password': 'testpassword'})
    return user

# Функция для отправки отзыва в базу данных
@sync_to_async
def send_review_to_site(username, flower_id, review_text, rating=None):
    try:
        user = User.objects.get(username=username)
        flower = Flower.objects.get(id=flower_id)
        review = Review.objects.create(user=user, flower=flower, review=review_text, rating=rating or 5)
        review.save()
        return True
    except User.DoesNotExist:
        print(f"Пользователь с именем {username} не найден")
        return False
    except Flower.DoesNotExist:
        print(f"Цветок с ID {flower_id} не найден")
        return False
    except Exception as e:
        print(f"Ошибка при сохранении отзыва: {str(e)}")
        return False

@sync_to_async# Функция для получения каталога цветов из базы данных
def get_flower_catalog():
    logging.info("Попытка загрузить каталог цветов из базы данных.")
    try:
        flowers = list(Flower.objects.all())  # Асинхронно получаем список цветов
        logging.info(f"Загружено {len(flowers)} цветов из базы данных.")
        return flowers
    except Exception as e:
        logging.error(f"Ошибка при получении каталога цветов: {str(e)}")
        return []

# Функция для получения заказов пользователя
@sync_to_async
def get_user_orders(username):
    try:
        user = User.objects.get(username=username)
        orders = Order.objects.filter(user=user)
        return orders
    except User.DoesNotExist:
        print(f"Пользователь с именем {username} не найден")
        return None
    except Exception as e:
        print(f"Ошибка при получении заказов пользователя: {str(e)}")
        return None

# Функция для создания заказа через бота
@sync_to_async
def create_order_in_db(user, cart_items):
    try:
        # Создаем новый заказ
        order = Order.objects.create(user=user, status='Оформлен')

        # Добавляем товары в заказ
        for item in cart_items:
            flower = Flower.objects.get(id=item['flower']['id'])
            quantity = item['quantity']
            price_per_item = flower.price
            order_item = OrderItem.objects.create(
                order=order, flower_name=flower.name, quantity=quantity, price_per_item=price_per_item
            )
            order_item.save()

        order.save()
        return order
    except Flower.DoesNotExist:
        print(f"Цветок с ID {item['flower']['id']} не найден")
        return None
    except Exception as e:
        print(f"Ошибка при создании заказа: {str(e)}")
        return None

# Функция для создания тестового заказа (если это необходимо)
@sync_to_async
def create_test_order():
    user = get_or_create_test_user()
    return create_order_in_db(user.id, [{'flower': {'id': 1}}, {'flower': {'id': 2}}], 'Test address')

# Функция для регистрации пользователя через бота
@sync_to_async
def register_user_via_bot(username, password, email):
    # Проверяем, что пользователь с таким именем не существует
    if User.objects.filter(username=username).exists():
        return f"Пользователь с именем {username} уже существует."

    # Проверяем, что пользователь с таким email не существует
    if User.objects.filter(email=email).exists():
        return "Пользователь с таким email уже существует."

    # Создаем нового пользователя
    try:
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        return True
    except Exception as e:
        print(f"Ошибка при создании пользователя: {str(e)}")
        return "Ошибка при регистрации."
