# shop/urls.py
from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import FlowerViewSet

router = DefaultRouter()
router.register(r'flowers', FlowerViewSet)

urlpatterns = [
    path('', views.flower_list, name='flower_list'),
    path('flower/<int:pk>/', views.flower_detail, name='flower_detail'),
    path('api/', include(router.urls)),]
