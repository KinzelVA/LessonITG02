# flowerdelivery/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView
from shop import views as shop_views  # Импортируем главную страницу
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('shop/', include('shop.urls')),  # Каталог цветов
    path('orders/', include('flower_orders.urls')),  # Страница для заказов
    path('reviews/', include('reviews.urls')),  # Страница для отзывов
    path('analytics/', include('analytics.urls')),  # Аналитика
    path('', shop_views.home, name='home'),  # Главная страница
    path('users/', include('users.urls')),
]

urlpatterns += [
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]

# Для загрузки статических и медиафайлов в режиме отладки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



