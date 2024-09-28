#flowerdelivery\flower_orders\urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.order_list, name='order_list'),  # Страница для заказов
]

# Для раздачи медиафайлов на локальном сервере
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

