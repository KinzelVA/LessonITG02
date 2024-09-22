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
        logger.info(f"Создание заказа: {request.data}")  # Логирование данных запроса

        data = request.data
        flower_ids = data.get('flower_ids', [])
        address = data.get('address', '')
        logger.info(f"Цветы для заказа: {flower_ids}")  # Логирование цветов

        # Проверяем наличие цветов
        flowers = Flower.objects.filter(id__in=flower_ids)
        if not flowers.exists():
            logger.error(f"Цветы не найдены: {flower_ids}")
            return Response({"error": "Цветы не найдены"}, status=status.HTTP_400_BAD_REQUEST)

        # Создаем заказ
        try:
            user_id = data.get('user')
            if not user_id:
                logger.error("Пользователь не указан")
                return Response({"error": "Пользователь не указан"}, status=status.HTTP_400_BAD_REQUEST)

            order = Order.objects.create(user_id=user_id, address=address)
            order.flowers.set(flowers)
            order.save()
            logger.info(f"Заказ создан: {order}")  # Логирование успешного создания

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
    orders = Order.objects.filter(user=request.user)
    return render(request, 'flower_orders/order_list.html', {'orders': orders})



