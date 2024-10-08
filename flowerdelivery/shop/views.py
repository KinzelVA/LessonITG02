# shop/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Flower
from rest_framework import viewsets
from .serializers import FlowerSerializer
from flower_orders.models import Order


class FlowerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Flower.objects.all()
    serializer_class = FlowerSerializer
def flower_list(request):
    flowers = Flower.objects.all()
    return render(request, 'shop/flower_list.html', {'flowers': flowers})


def flower_detail(request, pk):
    flower = get_object_or_404(Flower, pk=pk)
    return render(request, 'shop/flower_detail.html', {'flower': flower})


def home(request):
    # Здесь больше нет формы регистрации
    return render(request, 'shop/home.html')

def order_list(request):
    orders = Order.objects.all()  # Получаем все заказы
    return render(request, 'shop/order_list.html', {'orders': orders})
