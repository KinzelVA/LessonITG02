# shop/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.flower_list, name='flower_list'),
    path('flower/<int:pk>/', views.flower_detail, name='flower_detail'),
]