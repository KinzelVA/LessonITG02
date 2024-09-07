# flower_orders/views.py
from rest_framework import viewsets
from .models import Order
from .serializers import OrderSerializer
from django.shortcuts import render

# Страница заказов
def order_list(request):
    return render(request, 'flower_orders/order_list.html')

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
