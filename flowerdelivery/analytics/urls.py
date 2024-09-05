# analytics/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.analytics_view, name='analytics_view'),  # Страница аналитики
]
