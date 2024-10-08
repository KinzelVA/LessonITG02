# flowerdelivery\bot\bot_func.py
import os
import django
import sys
import logging
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from django.conf import settings
from shop.models import Flower  # Импорт моделей из вашего приложения
from reviews.models import Review
from flower_orders.models import Order

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
def get_flower_catalog():
    flowers = Flower.objects.all()
    flower_data = []
    for flower in flowers:
        image_url = None
        if flower.image:
            # Получаем абсолютный путь к изображению
            image_url = os.path.join(settings.MEDIA_ROOT, flower.image.name)

        flower_data.append({
            'id': flower.id,
            'name': flower.name,
            'price': flower.price,
            'description': flower.description or 'Описание отсутствует',
            'image_url': image_url
        })
    return flower_data

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

@sync_to_async
def get_user_orders(username):
    try:
        # Получаем все заказы пользователя по его username
        orders = Order.objects.filter(user__username=username)

        return list(orders)
    except Exception as e:
        print(f"Ошибка при получении заказов пользователя: {str(e)}")
        return []
# Функция для получения заказов пользователя
@sync_to_async
def create_order_in_db(user, cart_items):
    try:
        # Создаем новый заказ
        order = Order.objects.create(user=user, status='Оформлен')

        order_details = ""
        total_price = 0

        # Проходим по каждому элементу корзины
        for item in cart_items:
            flower = item['flower']  # Здесь уже будет объект Flower
            quantity = item['quantity']
            price_per_item = flower.price

            item_total = quantity * price_per_item
            total_price += item_total

            # Формируем строку с деталями для каждого элемента
            order_details += f"{flower.name} - {quantity} шт. по {price_per_item} руб., всего: {item_total} руб.\n"

        # Сохраняем общую информацию о заказе и детали
        order.total_price = total_price
        order.order_details = order_details
        order.save()

        return order
    except Exception as e:
        print(f"Ошибка при создании заказа: {str(e)}")
        return None

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
