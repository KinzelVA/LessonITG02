from django.urls import path
from . import views
from .views import UserRegisterAPIView, UserByUsernameAPIView

urlpatterns = [
    path('register/', UserRegisterAPIView.as_view(), name='register'),
    path('api/users/', UserByUsernameAPIView.as_view(), name='user_by_username'),
    path('login/', views.login_view, name='login'),
]
