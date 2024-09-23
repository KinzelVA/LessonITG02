#flowerdelivery\flower_orders\urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order_list'),  # Страница для заказов
]

