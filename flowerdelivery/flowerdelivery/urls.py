# flowerdelivery/urls.py
from django.contrib import admin
from django.urls import path, include
from reviews import views as review_views
from shop import views as shop_views
from flower_orders import views as order_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),  # API для пользователей
    path('shop/', include('shop.urls')),  # Каталог цветов
    path('orders/', order_views.order_list, name='order_list'),  # Страница для заказов
    path('api/', include('flower_orders.urls')),  # API для заказов
    path('api/', include('reviews.urls')),  # API для отзывов
    path('reviews/', review_views.review_list, name='review_list'),  # Страница для отзывов
    path('analytics/', include('analytics.urls')),  # Аналитика
    path('', shop_views.home, name='home'),  # Главная страница
]

# Для загрузки медиафайлов в режиме отладки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Маршрут для выхода
urlpatterns += [
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]



