# flower_orders/views.py
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Order
from .serializers import OrderSerializer
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import render
import requests

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

    def list(self, request, *args, **kwargs):
        username = request.query_params.get('username', None)
        if username:
            orders = Order.objects.filter(user__username=username)
            print("Заказы для пользователя", username, ":", orders)
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"detail": "Username not provided"}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        # Переопределяем метод create для обработки создания заказов
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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
