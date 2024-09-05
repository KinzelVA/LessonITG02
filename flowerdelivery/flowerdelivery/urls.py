from django.contrib import admin
from django.urls import path, include
from shop import views as shop_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),  # Роут для пользователей (если есть)
    path('shop/', include('shop.urls')),  # Роут для каталога цветов
    path('orders/', include('flower_orders.urls')),  # Роут для заказов
    path('reviews/', include('reviews.urls')),  # Роут для отзывов
    path('analytics/', include('analytics.urls')),  # Роут для аналитики
    path('', shop_views.home, name='home'),  # Главная страница
]




