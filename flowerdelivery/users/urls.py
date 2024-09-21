# users/urls.py
from django.urls import path
from . import views


urlpatterns = [

    # HTML-форма для регистрации
    path('register/', views.register, name='register'),

    # HTML-форма для входа в систему
    path('login/', views.login_view, name='login'),
]
