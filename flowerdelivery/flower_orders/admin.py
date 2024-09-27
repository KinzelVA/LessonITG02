from django.contrib import admin
from .models import Order

# Регистрация модели Flower


# Инлайн для редактирования товаров в заказе

# Регистрация модели Order
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status')
    search_fields = ('user__username', 'status')
    list_filter = ('status',)


# Регистрация модели OrderItem



