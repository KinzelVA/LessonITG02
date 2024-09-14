from django.contrib import admin
from django.urls import path, include
from shop import views as shop_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),  # Роут для пользователей (если есть)
    path('shop/', include('shop.urls')),  # Роут для каталога цветов
    path('orders/', include('flower_orders.urls')),  # Роут для заказов
    path('api/', include('reviews.urls')),  # Роут для отзывов
    path('analytics/', include('analytics.urls')),  # Роут для аналитики
    path('api/', include('flower_orders.urls')),  # API для заказов
    path('', shop_views.home, name='home'),  # Главная страница # Для загрузки изображений
    path('', include('reviews.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]




