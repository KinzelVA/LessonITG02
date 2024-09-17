# flower_orders/views.py
import requests
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from shop.models import Flower  # Импортируем модель цветов
from .serializers import OrderSerializer
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import render
import logging

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        username = self.request.query_params.get('username', None)
        if username:
            return Order.objects.filter(user__username=username)
        return Order.objects.none()

    def create(self, request, *args, **kwargs):
        data = request.data
        logger.info(f"Полученные данные: {data}")  # Логируем все полученные данные для отладки

        # Попробуем получить данные пользователя и адрес
        user_id = data.get('user')
        address = data.get('address', '')  # Используем пустую строку по умолчанию, если адрес не указан

        if not user_id:
            return Response({"error": "Пользователь не указан"}, status=status.HTTP_400_BAD_REQUEST)

        # Логируем информацию о пользователе и адресе
        logger.info(f"Полученный пользователь: {user_id}, Адрес: {address}")

        # Получаем список цветов
        flower_ids = data.get('flower_ids', [])
        logger.info(f"Полученные цветы: {flower_ids}")

        # Проверяем наличие цветов
        flowers = Flower.objects.filter(id__in=flower_ids)
        if not flowers.exists():
            return Response({"error": "Цветы не найдены"}, status=status.HTTP_400_BAD_REQUEST)

        # Создаем заказ
        try:
            order = Order.objects.create(user_id=user_id, address=address)
            order.flowers.set(flowers)  # Привязываем цветы к заказу
            order.save()

            # Логируем успешное создание заказа
            logger.info(f"Создан заказ: {order}")

            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Ошибка при создании заказа: {str(e)}")
            return Response({"error": "Ошибка при создании заказа"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        username = request.query_params.get('username', None)
        logger.info(f"Полученный username: {username}")  # Логируем для отладки
        if username:
            orders = Order.objects.filter(user__username=username)
            logger.info(f"Заказы для пользователя {username}: {orders}")  # Логируем заказы
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"detail": "Username not provided"}, status=status.HTTP_400_BAD_REQUEST)


def order_list(request):
    # Функция для получения списка заказов и рендеринга шаблона
    username = 'KinzelVA'  # Имя пользователя
    api_url = f"http://127.0.0.1:8000/api/orders/?username={username}"

    response = requests.get(api_url)

    if response.status_code == 200:
        orders = response.json()
        print("Полученные заказы через API:", orders)
        if isinstance(orders, list):
            # Если API возвращает список заказов
            print("Это список заказов:", orders)
        else:
            # Если API возвращает объект вместо списка
            print("API возвращает объект, а не список:", orders)
            orders = []
    else:
        orders = []
        print("Не удалось получить заказы через API")

    return render(request, 'flower_orders/order_list.html', {
        'orders': orders,  # Передаем список заказов в шаблон
    })
