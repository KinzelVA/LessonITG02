# shop/urls.py
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import FlowerViewSet
from .views import UserRegisterAPIView

router = DefaultRouter()
router.register(r'flowers', FlowerViewSet)

urlpatterns = [
    path('', views.flower_list, name='flower_list'),
    path('flower/<int:pk>/', views.flower_detail, name='flower_detail'),
    path('api/', include(router.urls)),
    path('api/register/', UserRegisterAPIView.as_view(), name='register'),  # Добавляем маршрут для регистрации
]

