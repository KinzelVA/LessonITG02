# flowerdelivery\bot\bot_func.py
import os
import django
import sys
import logging
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from shop.models import Flower  # Импорт моделей из вашего приложения
from reviews.models import Review
from flower_orders.models import OrderItem, Order

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
    try:
        # Получаем все цветы из базы данных
        flowers = Flower.objects.all()
        return list(flowers)
    except Exception as e:
        print(f"Ошибка при получении каталога цветов: {str(e)}")
        return []


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
        orders = Order.objects.filter(user__username=username).prefetch_related('items')
        print(f"Найденные заказы для {username}: {orders}")

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
        print(f"Созданный заказ: {order} (тип: {type(order)})")

        # Добавляем товары в заказ
        for item in cart_items:
            flower_id = item.get('flower', {}).get('id')
            print(f"ID цветка: {flower_id}")  # Проверим, что id цветка корректен
            if flower_id:
                # Получаем объект цветка
                flower = Flower.objects.get(id=flower_id)
                quantity = item['quantity']
                price_per_item = flower.price

                print(f"Добавляем цветок в заказ: {flower.name}, Количество: {quantity}, Цена: {price_per_item}")
                print(f"Тип переменной 'flower': {type(flower)}")  # Логирование типа flower

                # Логируем поля для создания OrderItem
                print(f"Поля для создания OrderItem: order_id={order.id}, flower={flower.name}, quantity={quantity}, price_per_item={price_per_item}")

                # Создаем элемент заказа с привязкой к цветку
                order_item = OrderItem.objects.create(
                    order=order,
                    flower=flower,  # Привязываем объект цветка к заказу
                    quantity=quantity,
                    price_per_item=price_per_item
                )
                order_item.save()

        order.save()
        return order
    except Flower.DoesNotExist:
        print(f"Цветок с ID {flower_id} не найден")
        return None
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
