# users/urls.py
from django.urls import path
from . import views
from .views import UserRegisterAPIView, UserByUsernameAPIView

urlpatterns = [
    # API маршрут для регистрации
    path('api/register/', UserRegisterAPIView.as_view(), name='api_register'),

    # API маршрут для получения пользователя по имени
    path('api/users/', UserByUsernameAPIView.as_view(), name='user_by_username'),

    # HTML-форма для регистрации
    path('register/', views.register, name='register'),

    # HTML-форма для входа в систему
    path('login/', views.login_view, name='login'),
]
