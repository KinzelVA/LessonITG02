# flower_orders/urls.py
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet
from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list, name='order_list'),  # Страница списка заказов
]

router = DefaultRouter()
router.register(r'orders', OrderViewSet)

urlpatterns = router.urls
