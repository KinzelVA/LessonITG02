# flower_orders/urls.py
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('', views.order_list, name='order_list'),
    path('api/', include(router.urls)),# Страница списка заказов
]




