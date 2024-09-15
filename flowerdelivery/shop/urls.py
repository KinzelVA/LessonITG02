# shop/urls.py
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import FlowerViewSet
from shop import views as shop_views


router = DefaultRouter()
router.register(r'flowers', FlowerViewSet, basename='flower')

urlpatterns = [
    path('', views.flower_list, name='flower_list'),
    path('flower/<int:pk>/', views.flower_detail, name='flower_detail'),
    path('api/', include(router.urls)),
    path('orders/', shop_views.order_list, name='order_list'),
]

