from django.urls import path
from . import views
from .views import UserRegisterAPIView


urlpatterns = [
    path('register/', UserRegisterAPIView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
]
